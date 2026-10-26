package mynet
{
   import flash.events.Event;
   import flash.events.IOErrorEvent;
   import flash.events.ProgressEvent;
   import flash.events.SecurityErrorEvent;
   import flash.net.Socket;
   import flash.utils.ByteArray;

   // The Multiplayer Everything launcher's lobby bridge, as a second transport next to RelayClient.
   // When the launcher starts the game with FlashVar lobby=1, connect this to 127.0.0.1:bridgePort
   // instead of the relay: the launcher made the room, so the mod shows no HOST/JOIN panel.
   // Each message is one JSON object with a NUL after it. Bridge events come out as the relay's own
   // star-mode text, so the mod's message handler stays the same for both transports:
   //   host    welcome -> onRoom(room)   go -> J|slot|name for every other player
   //           msg from slot -> G|slot|d   leave -> L|slot
   //   client  welcome -> W|slot   msg from the host -> d   host leave / end / closed -> onClose
   //   both    drop -> DR|slot, back -> BK|slot (the launcher keeps a dropped slot for 30 seconds)
   // send(msg) goes to everyone from the host, to the host from a client. From Bad Ice-Cream Online.
   // Usage:
   //   var b:LobbyBridge = new LobbyBridge(int(params.bridgePort), String(params.sessionToken));
   //   b.onRoom = ...; b.onMessage = yourRelayMessageHandler; b.onClose = ...;
   //   b.loaded() once the game can take the host's first message (past the intro); nobody gets
   //   "go" (so the host sees no J) until every player's game said loaded.
   public class LobbyBridge
   {
      public var onRoom:Function;      // (code:String) host: the room is ours
      public var onMessage:Function;   // (msg:String) relay-style messages, see above
      public var onClose:Function;     // (reason:String)
      public var slot:int = -1;
      public var room:String = "";
      public var isHost:Boolean = false;
      public var welcomed:Boolean = false;
      public var started:Boolean = false;  // "go" arrived
      public var seed:Number = 0;          // the same for every player

      private var sock:Socket;
      private var buf:ByteArray = new ByteArray();
      private var token:String;
      private var names:Object = {};
      private var slots:Array = [];
      private var sentLoaded:Boolean = false;
      private var finished:Boolean = false;

      public function LobbyBridge(port:int, sessionToken:String)
      {
         token = sessionToken;
         sock = new Socket();
         try
         {
            // compiled into some SWFs the setter throws #1056 in Ruffle desktop; the default timeout is fine
            sock.timeout = 8000;
         }
         catch(e:Error)
         {
         }
         sock.addEventListener(Event.CONNECT, function(e:Event):void
         {
            write("{\"t\":\"hello\",\"token\":" + NetJson.quote(token) + "}");
         });
         sock.addEventListener(Event.CLOSE, function(e:Event):void
         {
            finish("the launcher closed the connection");
         });
         sock.addEventListener(IOErrorEvent.IO_ERROR, function(e:IOErrorEvent):void
         {
            finish("can't reach the launcher (" + e.text + ")");
         });
         sock.addEventListener(SecurityErrorEvent.SECURITY_ERROR, function(e:SecurityErrorEvent):void
         {
            finish("blocked by Flash security (" + e.text + ")");
         });
         sock.addEventListener(ProgressEvent.SOCKET_DATA, onData);
         sock.connect("127.0.0.1", port);
      }

      public function nameOf(s:int) : String
      {
         return names[s] != null ? String(names[s]) : "Player " + (s + 1);
      }

      public function send(msg:String) : void
      {
         sendTo(isHost ? -1 : 0, msg);
      }

      // to: -1 everyone else, or a slot
      public function sendTo(to:int, msg:String) : void
      {
         if(welcomed)
         {
            write("{\"t\":\"send\",\"to\":" + to + ",\"d\":" + NetJson.quote(msg) + "}");
         }
      }

      public function loaded() : void
      {
         if(welcomed && !sentLoaded)
         {
            sentLoaded = true;
            write("{\"t\":\"loaded\"}");
         }
      }

      public function get isLoaded() : Boolean
      {
         return sentLoaded;
      }

      public function chat(text:String) : void
      {
         if(welcomed)
         {
            write("{\"t\":\"chat\",\"text\":" + NetJson.quote(text) + "}");
         }
      }

      // a line in the launcher's log, for bug reports
      public function log(text:String) : void
      {
         if(welcomed)
         {
            write("{\"t\":\"log\",\"text\":" + NetJson.quote(text) + "}");
         }
      }

      public function close() : void
      {
         finished = true;
         if(sock != null)
         {
            try
            {
               sock.close();
            }
            catch(e:Error)
            {
            }
            sock = null;
         }
      }

      private function write(text:String) : void
      {
         if(sock == null || !sock.connected)
         {
            return;
         }
         try
         {
            sock.writeUTFBytes(text);
            sock.writeByte(0);
            sock.flush();
         }
         catch(e:Error)
         {
            finish("send failed (" + e.message + ")");
         }
      }

      private function onData(e:ProgressEvent) : void
      {
         if(sock == null || sock.bytesAvailable == 0)
         {
            return;
         }
         sock.readBytes(buf, buf.length, sock.bytesAvailable);
         var start:int = 0;
         for(var k:int = 0; k < buf.length; k++)
         {
            if(buf[k] == 0)
            {
               buf.position = start;
               var text:String = buf.readUTFBytes(k - start);
               start = k + 1;
               if(text.length > 0)
               {
                  var m:* = null;
                  try
                  {
                     m = NetJson.parse(text);
                  }
                  catch(err:Error)
                  {
                     trace("[bridge] bad message (" + err.message + "): " + text.substr(0, 80));
                  }
                  if(m != null && typeof m == "object")
                  {
                     handle(m);
                  }
               }
               if(sock == null)
               {
                  return;
               }
            }
         }
         var rest:ByteArray = new ByteArray();
         if(start < buf.length)
         {
            buf.position = start;
            buf.readBytes(rest, 0, buf.length - start);
         }
         buf = rest;
      }

      private function handle(m:Object) : void
      {
         var t:String = String(m.t);
         var s:int = m.slot != null ? int(m.slot) : -1;
         if(m.name != null && s >= 0)
         {
            names[s] = clean(String(m.name));
         }
         if(t == "welcome")
         {
            welcomed = true;
            slot = int(m.slot);
            isHost = m.role == "host";
            room = m.room != null ? String(m.room) : "";
            seed = Number(m.seed);
            slots = [];
            var players:Array = m.players as Array;
            if(players != null)
            {
               for each(var p:Object in players)
               {
                  if(p != null && p.slot != null)
                  {
                     slots.push(int(p.slot));
                     if(p.name != null)
                     {
                        names[int(p.slot)] = clean(String(p.name));
                     }
                  }
               }
            }
            if(isHost)
            {
               if(onRoom != null)
               {
                  onRoom(room);
               }
            }
            else
            {
               emit("W|" + slot);
            }
         }
         else if(t == "go")
         {
            started = true;
            if(isHost)
            {
               for each(var other:int in slots)
               {
                  if(other != 0)
                  {
                     emit("J|" + other + "|" + nameOf(other));
                  }
               }
            }
         }
         else if(t == "msg")
         {
            if(typeof m.d != "string")
            {
               return;
            }
            var from:int = int(m.from);
            if(isHost && from > 0)
            {
               emit("G|" + from + "|" + m.d);
            }
            else if(!isHost && from == 0)
            {
               emit(String(m.d));
            }
         }
         else if(t == "drop" || t == "back")
         {
            if(isHost ? s > 0 : s == 0)
            {
               emit((t == "drop" ? "DR|" : "BK|") + s);
            }
         }
         else if(t == "leave")
         {
            if(isHost && s > 0)
            {
               emit("L|" + s);
            }
            else if(!isHost && s == 0)
            {
               finish("the host left");
            }
         }
         else if(t == "end")
         {
            if(!isHost)
            {
               finish("the host's game closed");
            }
         }
         else if(t == "closed")
         {
            finish("the room closed");
         }
      }

      private function emit(msg:String) : void
      {
         if(onMessage != null && !finished)
         {
            onMessage(msg);
         }
      }

      private function finish(reason:String) : void
      {
         if(finished)
         {
            return;
         }
         close();
         if(onClose != null)
         {
            onClose(reason);
         }
      }

      private static function clean(name:String) : String
      {
         return name.replace(/[|;,\x00\r\n]/g, "").substr(0, 24);
      }
   }
}
