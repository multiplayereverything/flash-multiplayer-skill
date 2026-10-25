// Template from Ultimate Crab Battle Online (SWF 6 safe: no try/catch, no getNextHighestDepth).
// Needs on _global.MYN: GAME_ID, VERSION, GLOBAL_RELAY (your relay, "host:port"), DEFAULT_PORT, relayTyped, myName, publicRoom, mi (from modinfo.as),
// log(), clean(), labLog(), onHostMsg(id,msg), onGuestMsg(msg), and a game hook where removeShips() is called.
// ---------------- relay: XMLSocket to the global mod relay (star mode) ----------------
// Host: RELAY|1|HOST|<game>|<version>|<public>|<name> -> ROOM|<code>|<max>, W|0, then G|<id>|<msg> from guests.
// Guest: RELAY|1|JOIN|<game>|<version>|<code>|<name> -> W|<id>, then the host's messages.
N.relayAddress = function()
{
   var N = _global.MYN;
   return N.relayTyped.length > 0 ? N.relayTyped : (N.mi.address.length > 0 ? N.mi.address : N.GLOBAL_RELAY);
};
N.splitAddress = function(addr)
{
   var c = addr.lastIndexOf(":");
   if(c < 1)
   {
      return {host:addr,port:N.DEFAULT_PORT};
   }
   return {host:addr.substr(0,c),port:Number(addr.substr(c + 1))};
};
N.openSocket = function(first)
{
   var N = _global.MYN;
   N.closeSocket();
   var a = N.splitAddress(N.relayAddress());
   var s = new XMLSocket();
   N.sock = s;
   N.sockOpen = false;
   N.firstLine = first;
   s.onConnect = function(ok)
   {
      var N = _global.MYN;
      if(this != N.sock)
      {
         return;
      }
      if(!ok)
      {
         N.endSession("Can't reach the server " + N.relayAddress() + ".");
         return;
      }
      N.sockOpen = true;
      this.send(N.firstLine);
   };
   s.onData = function(msg)
   {
      var N = _global.MYN;
      if(this == N.sock)
      {
         N.onRelay(String(msg));
      }
   };
   s.onClose = function()
   {
      var N = _global.MYN;
      if(this == N.sock)
      {
         N.endSession(N.lastError.length > 0 ? N.lastError : (N.role == 2 ? "The host closed the room." : "Connection closed."));
      }
   };
   N.log("connecting to " + a.host + ":" + a.port);
   if(!s.connect(a.host,a.port))
   {
      N.endSession("Can't open a connection to " + N.relayAddress() + ".");
   }
};
N.closeSocket = function()
{
   var N = _global.MYN;
   if(N.sock != undefined)
   {
      var s = N.sock;
      N.sock = undefined;
      s.close();
   }
   N.sockOpen = false;
};
N.send = function(m)
{
   var N = _global.MYN;
   if(N.sockOpen)
   {
      N.sock.send(m);
      N.sentCount++;
   }
};
N.sentCount = 0;
N.hostRoom = function()
{
   var N = _global.MYN;
   if(N.mi.tooOld && N.relayTyped.length == 0)
   {
      N.status = N.miStatusLine();
      return;
   }
   N.resetSession();
   N.role = 1;
   N.status = "Opening a room...";
   N.lastError = "";
   N.openSocket("RELAY|1|HOST|" + N.GAME_ID + "|" + N.VERSION + "|" + (N.publicRoom ? "1" : "0") + "|" + N.clean(N.myName,24) + "'s room");
};
N.joinRoom = function(code)
{
   var N = _global.MYN;
   code = N.clean(code,8).toUpperCase();
   if(code.length != 5)
   {
      N.status = "A room code has 5 letters.";
      return;
   }
   if(N.mi.tooOld && N.relayTyped.length == 0)
   {
      N.status = N.miStatusLine();
      return;
   }
   N.resetSession();
   N.role = 2;
   N.roomCode = code;
   N.status = "Joining " + code + "...";
   N.lastError = "";
   N.openSocket("RELAY|1|JOIN|" + N.GAME_ID + "|" + N.VERSION + "|" + code + "|" + N.clean(N.myName,24));
};
N.listRooms = function()
{
   var N = _global.MYN;
   if(N.role != 0)
   {
      return;
   }
   N.roomList = [];
   N.listStatus = "Looking for rooms...";
   var a = N.splitAddress(N.relayAddress());
   var s = new XMLSocket();
   N.listSock = s;
   s.onConnect = function(ok)
   {
      if(ok)
      {
         this.send("RELAY|1|LIST|" + _global.MYN.GAME_ID);
      }
      else
      {
         _global.MYN.listStatus = "Can't reach the server.";
      }
   };
   s.onData = function(msg)
   {
      var N = _global.MYN;
      msg = String(msg);
      this.close();
      if(msg.substr(0,5) != "LIST|")
      {
         N.listStatus = msg.substr(0,2) == "E|" ? msg.substr(2) : "The server didn't answer.";
         return;
      }
      var body = msg.substr(5);
      var rooms = body.length > 0 ? body.split(";") : [];
      var i = 0;
      while(i < rooms.length)
      {
         var p = rooms[i].split(",");
         if(p.length >= 4)
         {
            N.roomList.push({code:p[0],players:p[1],max:p[2],name:p.slice(3).join(",")});
         }
         i++;
      }
      N.listStatus = N.roomList.length == 0 ? "No open rooms. Host one!" : "";
   };
   s.connect(a.host,a.port);
};
N.leaveRoom = function()
{
   var N = _global.MYN;
   N.endSession("You left the room.");
};
N.resetSession = function()
{
   var N = _global.MYN;
   N.closeSocket();
   N.removeShips();
   N.players = new Object();
   N.myId = -1;
   N.roomCode = "";
   N.role = 0;
   N.hostDead = false;
   N.hostScore = undefined;
   N.snapPrev = new Object();
   N.lastRootSent = -1;
   N.pingMs = -1;
};
N.endSession = function(reason)
{
   var N = _global.MYN;
   var was = N.role;
   N.resetSession();
   N.status = reason;
   if(was != 0)
   {
      N.log("session ended: " + reason);
      N.labLog("ENDED " + reason);
   }
};

// one relay line
N.onRelay = function(m)
{
   var N = _global.MYN;
   var c = m.charAt(0);
   if(m.substr(0,5) == "ROOM|")
   {
      N.roomCode = m.split("|")[1];
      N.status = "Room " + N.roomCode + ". Send the code to your friends.";
      N.log("room " + N.roomCode);
      N.labLog("ROOM " + N.roomCode);
      return;
   }
   if(m.substr(0,2) == "W|")
   {
      N.myId = Number(m.substr(2));
      N.addPlayer(N.myId,N.myName);
      if(N.role == 2)
      {
         N.status = "Joined " + N.roomCode + ". Waiting for the host.";
         N.send("HELLO|" + N.clean(N.myName,24));
      }
      N.labLog("WELCOME " + N.myId);
      return;
   }
   if(m.substr(0,2) == "E|")
   {
      N.lastError = m.substr(2);
      N.log("relay error: " + N.lastError);
      return;
   }
   if(m == "X")
   {
      N.lastError = "The host closed the room.";
      return;
   }
   if(N.role == 1)
   {
      if(m.substr(0,2) == "J|")
      {
         var pj = m.split("|");
         N.addPlayer(Number(pj[1]),pj.slice(2).join("|"));
         N.sendRoster();
         N.snapPrev = new Object();
         N.lastRootSent = -1;
         N.log("joined: " + pj.slice(2).join("|"));
         return;
      }
      if(m.substr(0,2) == "L|")
      {
         N.dropPlayer(Number(m.substr(2)));
         N.sendRoster();
         return;
      }
      if(m.substr(0,2) == "G|")
      {
         var bar = m.indexOf("|",2);
         N.onGuestMsg(Number(m.substring(2,bar)),m.substr(bar + 1));
      }
      return;
   }
   if(N.role == 2)
   {
      N.onHostMsg(m);
   }
};

// ---------------- players ----------------
N.addPlayer = function(id, name)
{
   var N = _global.MYN;
   if(N.players[id] == undefined)
   {
      N.players[id] = {id:id,name:N.clean(name,24),x:0,y:0,tx:0,ty:0,seen:false};
   }
   else
   {
      N.players[id].name = N.clean(name,24);
   }
   N.players[id].slot = N.slotOf(id);
};
N.dropPlayer = function(id)
{
   var N = _global.MYN;
   var p = N.players[id];
   if(p != undefined)
   {
      if(p.mc != undefined)
      {
         p.mc.removeMovieClip();
      }
      delete N.players[id];
      N.log("left: " + p.name);
   }
};
N.playerCount = function()
{
   var N = _global.MYN;
   var cnt = 0;
   for(var k in N.players)
   {
      cnt++;
   }
   return cnt;
};
// colour slot 0..3 by join order (ids only grow)
N.slotOf = function(id)
{
   var N = _global.MYN;
   var ids = [];
   for(var k in N.players)
   {
      ids.push(Number(k));
   }
   ids.sort(function(a, b)
   {
      return a - b;
   });
   var i = 0;
   while(i < ids.length)
   {
      if(ids[i] == id)
      {
         return i % 4;
      }
      i++;
   }
   return 0;
};
N.sendRoster = function()
{
   var N = _global.MYN;
   var parts = [];
   for(var k in N.players)
   {
      parts.push(k + "," + N.players[k].name);
   }
   N.send("ROSTER|" + parts.join(";"));
   for(var k2 in N.players)
   {
      N.players[k2].slot = N.slotOf(Number(k2));
   }
};
N.applyRoster = function(body)
{
   var N = _global.MYN;
   var seen = new Object();
   var items = body.split(";");
   var i = 0;
   while(i < items.length)
   {
      var p = items[i].split(",");
      if(p.length >= 2)
      {
         N.addPlayer(Number(p[0]),p.slice(1).join(","));
         seen[Number(p[0])] = true;
      }
      i++;
   }
   for(var k in N.players)
   {
      if(seen[Number(k)] != true)
      {
         N.dropPlayer(Number(k));
      }
   }
   for(var k2 in N.players)
   {
      N.players[k2].slot = N.slotOf(Number(k2));
   }
};

// ping: a guest stamps Q|<ms>, the host answers A|<id>|<ms>
N.netTick = function()
{
   var N = _global.MYN;
   if(N.role == 2 && N.sockOpen && N.myId > 0 && N.frameNo % 68 == 0)
   {
      N.send("Q|" + getTimer());
   }
};
