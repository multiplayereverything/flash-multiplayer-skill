package mynet
{
   import flash.events.Event;
   import flash.events.IOErrorEvent;
   import flash.events.ProgressEvent;
   import flash.events.SecurityErrorEvent;
   import flash.net.Socket;
   import flash.utils.ByteArray;

   // Star-mode client for the global mod relay (mod-relay/relay.py). Copy into a mod and change the
   // package. NUL-terminated UTF-8 text, the same framing as XMLSocket; a raw Socket is used because
   // its AVM2 implementation is the more complete one in Ruffle. (Socket code from SH2's NetClient.)
   //
   //   var c:RelayClient = new RelayClient("mygame", "mygame-1");
   //   c.onRoom = function(code:String):void { ... show the code ... };   // host only
   //   c.onMessage = function(msg:String):void { ... W|id, J|id|name, G|id|msg, L|id, X ... };
   //   c.onClose = function(reason:String):void { ... };                   // "Relay: <E| reason>" on refusal
   //   c.host("relay.example.com:7790", "Alice", true);   or   c.join("relay.example.com:7790", "ABCDE", "Bob");
   //   c.send("hello");   // after W|: host -> every guest; guest -> host as G|<id>|hello
   public class RelayClient
   {
      public var onOpen:Function;      // () connected, handshake sent
      public var onRoom:Function;      // (code:String) the host's room code
      public var onMessage:Function;   // (msg:String) everything after the handshake
      public var onClose:Function;     // (reason:String)
      public var roomCode:String = "";

      private var game:String;
      private var version:String;
      private var sock:Socket;
      private var buf:ByteArray = new ByteArray();
      private var finished:Boolean = false;
      private var error:String = null;

      public function RelayClient(game:String, version:String)
      {
         super();
         this.game = game;
         this.version = version;
      }

      public function host(server:String, name:String, listed:Boolean) : void
      {
         open(server, "RELAY|1|HOST|" + game + "|" + version + "|" + (listed ? "1" : "0") + "|" + clean(name));
      }

      // DIRECT: a relay on the host's own PC, its legacy default room: H|name (host, answered with W|0, no ROOM|)
      // or J|name (friend, W|id); after that the same star protocol. The room takes up to 16 players and
      // checks no version: the host admits a friend only after its version message, and refuses extras.
      public function direct(server:String, asHost:Boolean, name:String) : void
      {
         open(server, (asHost ? "H|" : "J|") + clean(name));
      }

      public function join(server:String, code:String, name:String) : void
      {
         open(server, "RELAY|1|JOIN|" + game + "|" + version + "|" + code.toUpperCase().replace(/[^A-Z0-9]/g, "") + "|" + clean(name));
      }

      // Public rooms: done(rooms:Array of {code, players, max, name}, error:String). Uses its own connection.
      public static function list(server:String, game:String, done:Function) : void
      {
         var c:RelayClient = new RelayClient(game, "");
         c.onMessage = function(msg:String):void
         {
            c.onClose = null;
            c.close();
            var rooms:Array = [];
            for each(var row:String in msg.substr(5).split(";"))
            {
               var f:Array = row.split(",");
               if(f.length >= 4)
               {
                  rooms.push({"code":f[0], "players":int(f[1]), "max":int(f[2]), "name":f.slice(3).join(",")});
               }
            }
            done(msg.substr(0, 5) == "LIST|" ? rooms : null, msg.substr(0, 5) == "LIST|" ? null : msg);
         };
         c.onClose = function(reason:String):void
         {
            done(null, reason);
         };
         c.open(server, "RELAY|1|LIST|" + game);
      }

      // any other first line (RELAY|1|INFO|<game>): the answers arrive through onMessage, an E| as onClose
      public function ask(server:String, line:String) : void
      {
         open(server, line);
      }

      public function send(msg:String) : void
      {
         if(sock == null || !sock.connected)
         {
            return;
         }
         sock.writeUTFBytes(msg);
         sock.writeByte(0);
         sock.flush();
      }

      public function close() : void
      {
         if(sock != null && sock.connected)
         {
            try
            {
               sock.close();
            }
            catch(e:Error)
            {
            }
         }
         finish("Disconnected");
      }

      private function open(server:String, handshake:String) : void
      {
         var i:int = server.lastIndexOf(":");
         var host:String = i > 0 ? server.substr(0, i) : server;
         var port:int = i > 0 ? int(server.substr(i + 1)) : 7790;
         sock = new Socket();
         try
         {
            // compiled into this SWF, the setter throws #1056 in Ruffle desktop; the default timeout is fine
            sock.timeout = 8000;
         }
         catch(e:Error)
         {
         }
         sock.addEventListener(Event.CONNECT, function(e:Event):void
         {
            send(handshake);
            if(onOpen != null)
            {
               onOpen();
            }
         });
         sock.addEventListener(Event.CLOSE, function(e:Event):void
         {
            finish(error != null ? "Relay: " + error : "Connection closed");
         });
         sock.addEventListener(IOErrorEvent.IO_ERROR, function(e:IOErrorEvent):void
         {
            finish("Can't reach the server (" + e.text + ")");
         });
         sock.addEventListener(SecurityErrorEvent.SECURITY_ERROR, function(e:SecurityErrorEvent):void
         {
            finish("Blocked by Flash security (" + e.text + ")");
         });
         sock.addEventListener(ProgressEvent.SOCKET_DATA, onData);
         sock.connect(host, port);
      }

      private function onData(e:ProgressEvent) : void
      {
         if(sock == null || sock.bytesAvailable == 0)
         {
            return;
         }
         sock.readBytes(buf, buf.length, sock.bytesAvailable);
         var start:int = 0;
         var i:int = 0;
         while(i < buf.length)
         {
            if(buf[i] == 0)
            {
               buf.position = start;
               var msg:String = buf.readUTFBytes(i - start);
               start = i + 1;
               if(msg.substr(0, 5) == "ROOM|")
               {
                  roomCode = msg.split("|")[1];
                  if(onRoom != null)
                  {
                     onRoom(roomCode);
                  }
               }
               else if(msg.substr(0, 2) == "E|")
               {
                  // a room refusal is followed by a close; the legacy room's "a host is already connected" is
                  // not, so finish now with the relay's reason [Bad Ice-Cream]
                  error = msg.substr(2);
                  var s:Socket = sock;
                  finish("Relay: " + error);
                  try
                  {
                     s.close();
                  }
                  catch(err:Error)
                  {
                  }
                  return;
               }
               else if(msg.length > 0 && onMessage != null)
               {
                  onMessage(msg);
               }
               if(sock == null)
               {
                  return;
               }
            }
            i++;
         }
         var rest:ByteArray = new ByteArray();
         if(start < buf.length)
         {
            buf.position = start;
            buf.readBytes(rest, 0, buf.length - start);
         }
         buf = rest;
      }

      private function finish(reason:String) : void
      {
         if(finished)
         {
            return;
         }
         finished = true;
         sock = null;
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
