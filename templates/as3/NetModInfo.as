package mynet
{
   import flash.events.Event;
   import flash.events.IOErrorEvent;
   import flash.events.SecurityErrorEvent;
   import flash.net.SharedObject;
   import flash.net.URLLoader;
   import flash.net.URLRequest;
   import flash.utils.clearTimeout;
   import flash.utils.setTimeout;

   // Live mod information from github.com/multiplayereverything/mods-info: the central server's address,
   // the latest and oldest allowed versions and a notice, so a server move or an update needs no rebuild.
   // Same rules as the C# helper (global-mods-server/clients/ModInfo.cs) and mods-info/tools/validate.py:
   // anything invalid is ignored, and the last good copy (SharedObject "mynet_modinfo", data.modinfo) or the
   // built-in address is used. Nothing is downloaded besides the two JSON files, and nothing is run.
   public class NetModInfo
   {
      public static const GAME_ID:String = "mygame";
      // this build's version, compared with latest_version / min_version (numbers and dots)
      public static const VERSION:String = "1.0.0"; // = Net.MOD_VERSION
      // tried in order until one answers; the modinfo flashvar (test builds) replaces the list. Flash Player 32
      // refuses all of them for a local SWF (security error #2048), so the last resort is the relay itself:
      // RELAY|1|INFO|mygame on the server in use (typed, cached or built-in) answers with the same two files.
      public static const BASES:Array = ["https://raw.githubusercontent.com/multiplayereverything/mods-info/main/",
                                         "https://cdn.jsdelivr.net/gh/multiplayereverything/mods-info@main/"];
      private static const TIMEOUT_MS:int = 5000;

      public static var state:String = "idle";      // idle, loading, ok, failed
      public static var error:String = "";
      public static var source:String = "none";     // none, cache, download, relay
      public static var address:String = "";        // host:port from the files, or ""
      public static var serverStatus:String = "";
      public static var serverNotice:String = "";
      public static var latest:String = "";
      public static var minimum:String = "";
      public static var downloadUrl:String = "";
      public static var notice:String = "";
      public static var updateAvailable:Boolean = false;
      public static var tooOld:Boolean = false;
      public static var revision:int = 0;           // bumped on every change (the lobby redraws)
      public static var usedBase:String = "";

      private static var started:Boolean = false;

      // Once per launch: the cached copy at once, then a background download.
      public static function start() : void
      {
         // test builds skip it unless they name a test URL (--modinfo), like Baldi and Spooky's labs: the lab's
         // guard timing in Flash Player shifts when the download overlaps the session start
         var testUrl:String = Net.params.modinfo != null ? String(Net.params.modinfo) : "";
         if(started || (Net.LAB && testUrl.length == 0))
         {
            return;
         }
         started = true;
         loadCache();
         var bases:Array = testUrl.length > 0 ? [testUrl] : BASES;
         state = "loading";
         tryBase(bases, 0, []);
      }

      // The address to connect to: the player's own (typed) wins, then the downloaded or cached one, then built-in.
      public static function pick(typed:String, builtIn:String) : String
      {
         var t:String = trim(typed);
         return t.length > 0 ? t : (address.length > 0 ? address : builtIn);
      }

      public static function statusLine() : String
      {
         if(tooOld)
         {
            return "Online play needs version " + minimum + " or newer (you have " + VERSION + ")." + (downloadUrl.length > 0 ? " Get it at " + downloadUrl : "");
         }
         if(updateAvailable)
         {
            return "Update available: " + latest + " (you have " + VERSION + ")." + (downloadUrl.length > 0 ? " " + downloadUrl : "");
         }
         if(notice.length > 0)
         {
            return notice;
         }
         if(serverStatus == "maintenance")
         {
            return serverNotice.length > 0 ? serverNotice : "The server is down for maintenance.";
         }
         return serverNotice;
      }

      // One line for logs and the lab.
      public static function summary() : String
      {
         return "mods-info: " + state + (error.length > 0 ? " (" + error + ")" : "") + ", source " + source + (usedBase.length > 0 ? " from " + usedBase : "") +
                ", server '" + address + "'" + (statusLine().length > 0 ? ", says: " + statusLine() : "");
      }

      private static function tryBase(bases:Array, i:int, why:Array) : void
      {
         if(i >= bases.length)
         {
            askRelay(why);
            return;
         }
         var base:String = bases[i];
         fetch(base + "servers.json", function(servers:String, err:String):void
         {
            if(err != null)
            {
               why.push(base + ": " + err);
               tryBase(bases, i + 1, why);
               return;
            }
            fetch(base + "mods/" + GAME_ID + ".json", function(mod:String, err2:String):void
            {
               if(err2 != null)
               {
                  why.push(base + ": " + err2);
                  tryBase(bases, i + 1, why);
                  return;
               }
               var problem:String = apply(servers, mod, "download");
               if(problem != null)
               {
                  // a bad file is the same everywhere: don't try the mirror
                  fail(problem);
                  return;
               }
               usedBase = base;
               state = "ok";
               error = "";
               saveCache(servers, mod);
               Net.log(summary());
               Net.infoChanged();
            });
         });
      }

      private static function fail(reason:String) : void
      {
         state = "failed";
         error = reason;
         revision++;
         Net.log(summary());
         Net.infoChanged();
      }

      // Asks the relay in use for the two files: INFO|servers|<json> then INFO|mod|<json>.
      private static function askRelay(why:Array, retried:Boolean = false) : void
      {
         var addr:String = Net.address;
         if(addr.length == 0)
         {
            why.push("no server to ask");
            fail(why.join("; "));
            return;
         }
         var asker:RelayClient = new RelayClient(GAME_ID, "");
         var serversText:String = null;
         var over:Boolean = false;
         var timer:uint = 0;
         var stop:Function = function():void
         {
            over = true;
            clearTimeout(timer);
            asker.onClose = null;
            asker.close();
         };
         timer = setTimeout(function():void
         {
            if(!over)
            {
               stop();
               why.push("relay " + addr + ": timed out");
               fail(why.join("; "));
            }
         }, TIMEOUT_MS);
         asker.onMessage = function(msg:String):void
         {
            if(over)
            {
               return;
            }
            if(msg.indexOf("INFO|servers|") == 0)
            {
               serversText = msg.substr(13);
               return;
            }
            stop();
            if(msg.indexOf("INFO|mod|") == 0 && serversText != null)
            {
               var problem:String = apply(serversText, msg.substr(9), "relay");
               if(problem != null)
               {
                  fail(problem);
                  return;
               }
               usedBase = "relay " + addr;
               state = "ok";
               error = "";
               saveCache(serversText, msg.substr(9));
               Net.log(summary());
               Net.infoChanged();
               return;
            }
            why.push("relay " + addr + ": " + (msg.substr(0, 2) == "E|" ? msg.substr(2) : "unexpected answer"));
            fail(why.join("; "));
         };
         asker.onClose = function(reason:String):void
         {
            if(!over)
            {
               stop();
               // a relay that just started may not have fetched mods-info yet: ask once more in 5 s
               if(!retried && reason.indexOf("No mods-info") >= 0)
               {
                  setTimeout(function():void
                  {
                     askRelay(why, true);
                  }, 5000);
                  return;
               }
               why.push("relay " + addr + ": " + reason);
               fail(why.join("; "));
            }
         };
         asker.ask(addr, "RELAY|1|INFO|" + GAME_ID);
      }

      // done(text, null) or done(null, reason)
      private static function fetch(url:String, done:Function) : void
      {
         var loader:URLLoader = new URLLoader();
         var finished:Boolean = false;
         var timer:uint = 0;
         var finish:Function = function(text:String, err:String):void
         {
            if(finished)
            {
               return;
            }
            finished = true;
            clearTimeout(timer);
            try
            {
               loader.close();
            }
            catch(e:Error)
            {
            }
            done(text, err);
         };
         loader.addEventListener(Event.COMPLETE, function(e:Event):void
         {
            var s:String = String(loader.data);
            finish(s.length > 65536 ? null : s, s.length > 65536 ? "file too large" : null);
         });
         loader.addEventListener(IOErrorEvent.IO_ERROR, function(e:IOErrorEvent):void
         {
            finish(null, "IO error " + e.text);
         });
         loader.addEventListener(SecurityErrorEvent.SECURITY_ERROR, function(e:SecurityErrorEvent):void
         {
            finish(null, "security error " + e.text);
         });
         timer = setTimeout(function():void
         {
            finish(null, "timed out");
         }, TIMEOUT_MS);
         try
         {
            loader.load(new URLRequest(url));
         }
         catch(e:Error)
         {
            finish(null, "refused: " + e.message);
         }
      }

      private static function loadCache() : void
      {
         try
         {
            var so:SharedObject = SharedObject.getLocal("mynet_modinfo");
            if(so.data.modinfo && so.data.modinfo.servers && so.data.modinfo.mod)
            {
               apply(String(so.data.modinfo.servers), String(so.data.modinfo.mod), "cache");
            }
         }
         catch(e:Error)
         {
         }
      }

      private static function saveCache(servers:String, mod:String) : void
      {
         try
         {
            var so:SharedObject = SharedObject.getLocal("mynet_modinfo");
            so.data.modinfo = {"servers":servers, "mod":mod};
            so.flush();
         }
         catch(e:Error)
         {
         }
      }

      // Checks both files; on success replaces the current values and returns null, else the reason.
      private static function apply(serversText:String, modText:String, from:String) : String
      {
         var sv:Object;
         var md:Object;
         try
         {
            sv = NetJson.parse(serversText);
            md = NetJson.parse(modText);
         }
         catch(e:Error)
         {
            return "not valid JSON: " + e.message;
         }
         if(sv == null || sv.schema !== 1)
         {
            return "servers.json: schema must be 1";
         }
         if(md == null || md.schema !== 1)
         {
            return "mod file: schema must be 1";
         }
         var list:Array = sv.servers as Array;
         if(list == null || list.length == 0)
         {
            return "servers.json: no servers";
         }
         var byId:Object = {};
         for each(var s:Object in list)
         {
            var sid:String = str(s, "id");
            var saddr:String = str(s, "address");
            var sstat:String = str(s, "status");
            if(!/^[a-z0-9][a-z0-9-]{0,31}$/.test(sid) || byId.hasOwnProperty(sid))
            {
               return "servers.json: bad or duplicate id";
            }
            if(!validAddress(saddr))
            {
               return "servers.json: bad address for " + sid;
            }
            if(sstat != "online" && sstat != "offline" && sstat != "maintenance")
            {
               return "servers.json: bad status for " + sid;
            }
            if(sstat == "online" && saddr.length == 0)
            {
               return "servers.json: online server " + sid + " has no address";
            }
            if(!oneLine(str(s, "name")) || !oneLine(str(s, "notice")))
            {
               return "servers.json: bad text for " + sid;
            }
            byId[sid] = s;
         }
         for each(var key:String in ["id", "name", "game", "engine", "status", "latest_version", "min_version", "protocol", "download_url", "changelog_url", "relay", "notice", "updated"])
         {
            if(!md.hasOwnProperty(key))
            {
               return "mod file: missing " + key;
            }
         }
         if(str(md, "id") != GAME_ID)
         {
            return "mod file is for '" + str(md, "id") + "', not '" + GAME_ID + "'";
         }
         var lat:String = str(md, "latest_version");
         var mn:String = str(md, "min_version");
         if(!validVersion(lat) || !validVersion(mn))
         {
            return "mod file: bad version";
         }
         if(compare(mn, lat) > 0)
         {
            return "mod file: min_version is above latest_version";
         }
         var dl:String = str(md, "download_url");
         if(!validUrl(dl) || !validUrl(str(md, "changelog_url")))
         {
            return "mod file: links must be https://";
         }
         for each(var tkey:String in ["name", "game", "engine", "protocol", "notice"])
         {
            if(!oneLine(str(md, tkey)))
            {
               return "mod file: bad " + tkey;
            }
         }
         var relay:Object = md.relay;
         if(relay == null || typeof relay != "object" || relay is Array)
         {
            return "mod file: relay must be an object";
         }
         if(str(relay, "mode") != "star" && str(relay, "mode") != "tunnel")
         {
            return "mod file: bad relay.mode";
         }
         var mp:* = relay.max_players;
         if(!(mp is Number) || mp < 2 || mp > 16 || mp != Math.floor(mp))
         {
            return "mod file: bad relay.max_players";
         }
         if(!byId.hasOwnProperty(str(relay, "server")))
         {
            return "mod file: relay.server isn't in servers.json";
         }
         var own:String = str(relay, "address");
         if(!validAddress(own))
         {
            return "mod file: bad relay.address";
         }
         var chosen:Object = byId[str(relay, "server")];
         source = from;
         address = own.length > 0 ? own : str(chosen, "address");
         serverStatus = str(chosen, "status");
         serverNotice = str(chosen, "notice");
         latest = lat;
         minimum = mn;
         downloadUrl = dl;
         notice = str(md, "notice");
         updateAvailable = compare(VERSION, lat) < 0;
         tooOld = compare(VERSION, mn) < 0;
         revision++;
         return null;
      }

      // numeric dotted compare: "0.10" > "0.9", "1" == "1.0"
      public static function compare(a:String, b:String) : int
      {
         var x:Array = a.split(".");
         var y:Array = b.split(".");
         for(var i:int = 0; i < Math.max(x.length, y.length); i++)
         {
            var p:Number = i < x.length ? Number(x[i]) : 0;
            var q:Number = i < y.length ? Number(y[i]) : 0;
            if(p != q)
            {
               return p < q ? -1 : 1;
            }
         }
         return 0;
      }

      private static function validVersion(v:String) : Boolean
      {
         return /^[0-9]+(\.[0-9]+){0,3}$/.test(v);
      }

      private static function validAddress(a:String) : Boolean
      {
         if(a.length == 0)
         {
            return true;
         }
         if(!/^[A-Za-z0-9.\-]{1,253}:[0-9]{1,5}$/.test(a))
         {
            return false;
         }
         var port:int = int(a.substr(a.lastIndexOf(":") + 1));
         return port >= 1 && port <= 65535;
      }

      private static function validUrl(u:String) : Boolean
      {
         return u.length == 0 || (u.indexOf("https://") == 0 && u.length <= 500 && oneLine(u));
      }

      private static function oneLine(t:String) : Boolean
      {
         return t.length <= 200 && t.indexOf("\n") < 0 && t.indexOf("\r") < 0;
      }

      private static function str(o:Object, key:String) : String
      {
         return o != null && o.hasOwnProperty(key) && o[key] is String ? String(o[key]) : "";
      }

      private static function trim(s:String) : String
      {
         return s == null ? "" : s.replace(/^\s+|\s+$/g, "");
      }
   }
}
