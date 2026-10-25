// Set N.GAME_ID = "<your relay id>" in your net code before miStart(): every request below uses it.
// Mod template: mods-info (github.com/multiplayereverything/mods-info), from the global-mod-relay skill's AS2 example.
// N.miStart() runs once at boot (not in lab builds unless a test URL is given).
var N = _global.MYN;
   N.MI_VERSION = "1";
   N.MI_BASES = _global.MY_MODINFO != undefined ? [_global.MY_MODINFO] : ["https://raw.githubusercontent.com/multiplayereverything/mods-info/main/","https://cdn.jsdelivr.net/gh/multiplayereverything/mods-info@main/"];
   N.mi = {state:"idle",error:"",source:"none",address:"",serverStatus:"",serverNotice:"",latest:"",minimum:"",downloadUrl:"",notice:"",updateAvailable:false,tooOld:false,used:""};
   N.trimText = function(t)
   {
      if(t == undefined)
      {
         return "";
      }
      t = String(t);
      while(t.length > 0 && " \t\r\n".indexOf(t.charAt(0)) >= 0)
      {
         t = t.substr(1);
      }
      while(t.length > 0 && " \t\r\n".indexOf(t.charAt(t.length - 1)) >= 0)
      {
         t = t.substr(0,t.length - 1);
      }
      return t;
   };
   // the server in use: a relay= FlashVar (this run only, never saved), the player's own (typed), else
   // mods-info's, else the built-in central relay. Online on the central relay is the default.
   N.relayAddress = function()
   {
      var N = _global.MYN;
      if(N.relayFlash != undefined && N.relayFlash.length > 0)
      {
         return N.relayFlash;
      }
      return N.relayTyped.length > 0 ? N.relayTyped : (N.mi.address.length > 0 ? N.mi.address : N.GLOBAL_RELAY);
   };
   // setting the automatic address (or "") clears the player's own
   N.setRelay = function(v)
   {
      var N = _global.MYN;
      v = N.trimText(v);
      var auto = N.mi.address.length > 0 ? N.mi.address : N.GLOBAL_RELAY;
      N.relayTyped = v.length == 0 || v == auto ? "" : v.substr(0,128);
      N.prefs.data.relay = N.relayTyped;
   };
   N.miStatusLine = function()
   {
      var m = _global.MYN.mi;
      var V = _global.MYN.MI_VERSION;
      if(m.tooOld)
      {
         return "Online play needs version " + m.minimum + " or newer (you have " + V + ")." + (m.downloadUrl.length > 0 ? " Get it at " + m.downloadUrl : "");
      }
      if(m.updateAvailable)
      {
         return "Update available: " + m.latest + " (you have " + V + ")." + (m.downloadUrl.length > 0 ? " " + m.downloadUrl : "");
      }
      if(m.notice.length > 0)
      {
         return m.notice;
      }
      if(m.serverStatus == "maintenance")
      {
         return m.serverNotice.length > 0 ? m.serverNotice : "The server is down for maintenance.";
      }
      return m.serverNotice;
   };
   N.miSummary = function()
   {
      var N = _global.MYN;
      var m = N.mi;
      var line = N.miStatusLine();
      return "mods-info: " + m.state + (m.error.length > 0 ? " (" + m.error + ")" : "") + ", source " + m.source + (m.used.length > 0 ? " from " + m.used : "") + ", server '" + m.address + "'" + (line.length > 0 ? ", says: " + line : "");
   };
   // minimal JSON reader: objects, arrays, strings, numbers, true/false/null; throws a string on bad input
   N.jsonParse = function(text)
   {
      var st = {s:String(text),i:0};
      var space = function()
      {
         while(st.i < st.s.length && " \t\r\n".indexOf(st.s.charAt(st.i)) >= 0)
         {
            st.i++;
         }
      };
      var str = function()
      {
         var out = "";
         st.i++;
         while(st.i < st.s.length)
         {
            var c = st.s.charAt(st.i++);
            if(c == "\"")
            {
               return out;
            }
            if(c != "\\")
            {
               out += c;
               continue;
            }
            var e = st.s.charAt(st.i++);
            if(e == "n")
            {
               out += "\n";
            }
            else if(e == "r")
            {
               out += "\r";
            }
            else if(e == "t")
            {
               out += "\t";
            }
            else if(e == "u")
            {
               out += String.fromCharCode(parseInt(st.s.substr(st.i,4),16));
               st.i += 4;
            }
            else
            {
               out += e;
            }
         }
         throw "unterminated string";
      };
      var value = function()
      {
         space();
         if(st.i >= st.s.length)
         {
            throw "unexpected end";
         }
         var c = st.s.charAt(st.i);
         if(c == "{")
         {
            var o = new Object();
            st.i++;
            space();
            if(st.s.charAt(st.i) == "}")
            {
               st.i++;
               return o;
            }
            while(true)
            {
               space();
               if(st.s.charAt(st.i) != "\"")
               {
                  throw "expected a key at " + st.i;
               }
               var k = str();
               space();
               if(st.s.charAt(st.i) != ":")
               {
                  throw "expected : at " + st.i;
               }
               st.i++;
               o[k] = value();
               space();
               if(st.s.charAt(st.i) == ",")
               {
                  st.i++;
                  continue;
               }
               if(st.s.charAt(st.i) == "}")
               {
                  st.i++;
                  return o;
               }
               throw "expected , or } at " + st.i;
            }
         }
         if(c == "[")
         {
            var a = [];
            st.i++;
            space();
            if(st.s.charAt(st.i) == "]")
            {
               st.i++;
               return a;
            }
            while(true)
            {
               a.push(value());
               space();
               if(st.s.charAt(st.i) == ",")
               {
                  st.i++;
                  continue;
               }
               if(st.s.charAt(st.i) == "]")
               {
                  st.i++;
                  return a;
               }
               throw "expected , or ] at " + st.i;
            }
         }
         if(c == "\"")
         {
            return str();
         }
         if(st.s.substr(st.i,4) == "true")
         {
            st.i += 4;
            return true;
         }
         if(st.s.substr(st.i,5) == "false")
         {
            st.i += 5;
            return false;
         }
         if(st.s.substr(st.i,4) == "null")
         {
            st.i += 4;
            return null;
         }
         var start = st.i;
         while(st.i < st.s.length && "+-0123456789.eE".indexOf(st.s.charAt(st.i)) >= 0)
         {
            st.i++;
         }
         var n = Number(st.s.substring(start,st.i));
         if(st.i == start || isNaN(n))
         {
            throw "bad value at " + start;
         }
         return n;
      };
      var v = value();
      space();
      if(st.i != st.s.length)
      {
         throw "extra text at " + st.i;
      }
      return v;
   };
   // AS2 has no RegExp: the format checks are spelled out
   N.miOnly = function(t, allowed)
   {
      var i = 0;
      while(i < t.length)
      {
         if(allowed.indexOf(t.charAt(i)) < 0)
         {
            return false;
         }
         i++;
      }
      return true;
   };
   N.miId = function(t)
   {
      return typeof t == "string" && t.length >= 1 && t.length <= 32 && t.charAt(0) != "-" && _global.MYN.miOnly(t,"abcdefghijklmnopqrstuvwxyz0123456789-");
   };
   N.miVersion = function(t)
   {
      if(typeof t != "string" || t.length == 0)
      {
         return false;
      }
      var parts = t.split(".");
      if(parts.length > 4)
      {
         return false;
      }
      var i = 0;
      while(i < parts.length)
      {
         if(parts[i].length == 0 || !_global.MYN.miOnly(parts[i],"0123456789"))
         {
            return false;
         }
         i++;
      }
      return true;
   };
   N.miAddress = function(t)
   {
      if(t.length == 0)
      {
         return true;
      }
      var c = t.lastIndexOf(":");
      if(c < 1 || c > 253)
      {
         return false;
      }
      var host = t.substr(0,c);
      var port = t.substr(c + 1);
      if(port.length < 1 || port.length > 5 || !_global.MYN.miOnly(port,"0123456789") || Number(port) < 1 || Number(port) > 65535)
      {
         return false;
      }
      return _global.MYN.miOnly(host,"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-");
   };
   N.miLine = function(t)
   {
      return t.length <= 200 && t.indexOf("\n") < 0 && t.indexOf("\r") < 0;
   };
   N.miUrl = function(t)
   {
      return t.length == 0 || t.indexOf("https://") == 0 && t.length <= 500 && _global.MYN.miLine(t);
   };
   N.miStr = function(o, k)
   {
      return o != undefined && o != null && typeof o[k] == "string" ? o[k] : "";
   };
   N.miCompare = function(a, b)
   {
      var x = a.split(".");
      var y = b.split(".");
      var n = Math.max(x.length,y.length);
      var i = 0;
      while(i < n)
      {
         var p = i < x.length ? Number(x[i]) : 0;
         var q = i < y.length ? Number(y[i]) : 0;
         if(p != q)
         {
            return p < q ? -1 : 1;
         }
         i++;
      }
      return 0;
   };
   // checks both files; on success replaces N.mi's values and returns null, else the reason
   N.miApply = function(serversText, modText, from)
   {
      var N = _global.MYN;
      var S = N.miStr;
      var sv;
      var md;
      try
      {
         sv = N.jsonParse(serversText);
         md = N.jsonParse(modText);
      }
      catch(err)
      {
         return "not valid JSON: " + err;
      }
      if(sv == null || sv.schema !== 1)
      {
         return "servers.json: schema must be 1";
      }
      if(md == null || md.schema !== 1)
      {
         return "mod file: schema must be 1";
      }
      var list = sv.servers;
      if(!(list instanceof Array) || list.length == 0)
      {
         return "servers.json: no servers";
      }
      var byId = new Object();
      var i = 0;
      while(i < list.length)
      {
         var sr = list[i];
         var sid = S(sr,"id");
         if(!N.miId(sid) || byId[sid] != undefined)
         {
            return "servers.json: bad or duplicate id";
         }
         if(!N.miAddress(S(sr,"address")))
         {
            return "servers.json: bad address for " + sid;
         }
         var stt = S(sr,"status");
         if(stt != "online" && stt != "offline" && stt != "maintenance")
         {
            return "servers.json: bad status for " + sid;
         }
         if(stt == "online" && S(sr,"address").length == 0)
         {
            return "servers.json: online server " + sid + " has no address";
         }
         if(!N.miLine(S(sr,"name")) || !N.miLine(S(sr,"notice")))
         {
            return "servers.json: bad text for " + sid;
         }
         byId[sid] = sr;
         i++;
      }
      var keys = ["id","name","game","engine","status","latest_version","min_version","protocol","download_url","changelog_url","relay","notice","updated"];
      i = 0;
      while(i < keys.length)
      {
         if(md[keys[i]] == undefined)
         {
            return "mod file: missing " + keys[i];
         }
         i++;
      }
      if(S(md,"id") != N.GAME_ID)
      {
         return "mod file is for '" + S(md,"id") + "', not '" + N.GAME_ID + "'";
      }
      var lat = S(md,"latest_version");
      var mn = S(md,"min_version");
      if(!N.miVersion(lat) || !N.miVersion(mn))
      {
         return "mod file: bad version";
      }
      if(N.miCompare(mn,lat) > 0)
      {
         return "mod file: min_version is above latest_version";
      }
      if(!N.miUrl(S(md,"download_url")) || !N.miUrl(S(md,"changelog_url")))
      {
         return "mod file: links must be https://";
      }
      var tk = ["name","game","engine","protocol","notice"];
      i = 0;
      while(i < tk.length)
      {
         if(!N.miLine(S(md,tk[i])))
         {
            return "mod file: bad " + tk[i];
         }
         i++;
      }
      var r = md.relay;
      if(r == null || typeof r != "object" || r instanceof Array)
      {
         return "mod file: relay must be an object";
      }
      if(S(r,"mode") != "star" && S(r,"mode") != "tunnel")
      {
         return "mod file: bad relay.mode";
      }
      if(typeof r.max_players != "number" || r.max_players < 2 || r.max_players > 16 || r.max_players != Math.floor(r.max_players))
      {
         return "mod file: bad relay.max_players";
      }
      if(byId[S(r,"server")] == undefined)
      {
         return "mod file: relay.server isn't in servers.json";
      }
      if(!N.miAddress(S(r,"address")))
      {
         return "mod file: bad relay.address";
      }
      var chosen = byId[S(r,"server")];
      var m = N.mi;
      m.source = from;
      m.address = S(r,"address").length > 0 ? S(r,"address") : S(chosen,"address");
      m.serverStatus = S(chosen,"status");
      m.serverNotice = S(chosen,"notice");
      m.latest = lat;
      m.minimum = mn;
      m.downloadUrl = S(md,"download_url");
      m.notice = S(md,"notice");
      m.updateAvailable = N.miCompare(N.MI_VERSION,lat) < 0;
      m.tooOld = N.miCompare(N.MI_VERSION,mn) < 0;
      return null;
   };
   N.miDone = function(state, error, servers, mod, used)
   {
      var N = _global.MYN;
      N.mi.state = state;
      N.mi.error = error;
      if(state == "ok")
      {
         N.mi.used = used;
         N.prefs.data.modinfo = {servers:servers,mod:mod};
         N.prefs.flush();
      }
      N.log(N.miSummary());
      
   };
   // done(text, undefined) or done(undefined, reason)
   N.miFetch = function(url, done)
   {
      var lv = new LoadVars();
      var over = false;
      var iv;
      lv.onData = function(src)
      {
         if(over)
         {
            return;
         }
         over = true;
         clearInterval(iv);
         if(src == undefined)
         {
            done(undefined,"refused or not found");
         }
         else if(src.length > 65536)
         {
            done(undefined,"file too large");
         }
         else
         {
            done(src,undefined);
         }
      };
      iv = setInterval(function()
      {
         if(!over)
         {
            over = true;
            clearInterval(iv);
            done(undefined,"timed out");
         }
      },5000);
      lv.load(url);
   };
   N.miTry = function(i, why)
   {
      var N = _global.MYN;
      if(i >= N.MI_BASES.length)
      {
         N.miAskRelay(why);
         return;
      }
      var base = N.MI_BASES[i];
      N.miFetch(base + "servers.json",function(servers, err)
      {
         if(err != undefined)
         {
            why.push(base + ": " + err);
            _global.MYN.miTry(i + 1,why);
            return;
         }
         _global.MYN.miFetch(base + "mods/" + _global.MYN.GAME_ID + ".json",function(mod, err2)
         {
            var N = _global.MYN;
            if(err2 != undefined)
            {
               why.push(base + ": " + err2);
               N.miTry(i + 1,why);
               return;
            }
            var problem = N.miApply(servers,mod,"download");
            N.miDone(problem == null ? "ok" : "failed",problem == null ? "" : problem,servers,mod,base);
         });
      });
   };
   // the relay in use answers INFO|servers|<json> then INFO|mod|<json>
   N.miAskRelay = function(why, retried)
   {
      var N = _global.MYN;
      var addr = N.relayAddress();
      if(addr.length == 0)
      {
         why.push("no server to ask");
         N.miDone("failed",why.join("; "));
         return;
      }
      var a = addr.split(":");
      var ask = new XMLSocket();
      var over = false;
      var serversText;
      var iv;
      // not "stop": AS2 compiles stop() to the timeline's Stop action
      var endAsk = function()
      {
         over = true;
         clearInterval(iv);
         ask.close();
      };
      iv = setInterval(function()
      {
         if(!over)
         {
            endAsk();
            why.push("relay " + addr + ": timed out");
            _global.MYN.miDone("failed",why.join("; "));
         }
      },5000);
      ask.onConnect = function(ok)
      {
         if(ok)
         {
            ask.send("RELAY|1|INFO|" + _global.MYN.GAME_ID);
         }
         else if(!over)
         {
            endAsk();
            why.push("relay " + addr + ": can't connect");
            _global.MYN.miDone("failed",why.join("; "));
         }
      };
      ask.onData = function(msg)
      {
         var N = _global.MYN;
         if(over)
         {
            return;
         }
         if(msg.substr(0,13) == "INFO|servers|")
         {
            serversText = msg.substr(13);
            return;
         }
         endAsk();
         if(msg.substr(0,9) == "INFO|mod|" && serversText != undefined)
         {
            var problem = N.miApply(serversText,msg.substr(9),"relay");
            N.miDone(problem == null ? "ok" : "failed",problem == null ? "" : problem,serversText,msg.substr(9),"relay " + addr);
            return;
         }
         // a relay that just started may not have fetched mods-info yet: ask once more in 5 s
         if(retried != true && msg.substr(0,14) == "E|No mods-info")
         {
            var again = setInterval(function()
            {
               clearInterval(again);
               _global.MYN.miAskRelay(why,true);
            },5000);
            return;
         }
         why.push("relay " + addr + ": " + (msg.substr(0,2) == "E|" ? msg.substr(2) : "unexpected answer"));
         N.miDone("failed",why.join("; "));
      };
      ask.onClose = function()
      {
         if(!over)
         {
            endAsk();
            why.push("relay " + addr + ": closed");
            _global.MYN.miDone("failed",why.join("; "));
         }
      };
      ask.connect(a[0],a.length > 1 ? Number(a[1]) : 25569);
   };
   // once per launch: the cached copy at once, then the download in the background
   N.miStart = function()
   {
      var N = _global.MYN;
      var c = N.prefs.data.modinfo;
      if(c != undefined && c.servers != undefined && c.mod != undefined && N.miApply(c.servers,c.mod,"cache") == null)
      {
         N.mi.state = "cached";
      }
      N.mi.state = "loading";
      N.miTry(0,[]);
   };
