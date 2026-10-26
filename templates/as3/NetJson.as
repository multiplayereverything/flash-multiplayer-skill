package mynet
{
   // Minimal JSON, so the build doesn't depend on the player having the built-in JSON class (SWF 9 has
   // none): parse() reads objects, arrays, strings, numbers, true/false/null; quote() writes a string
   // literal (for LobbyBridge's messages). Strings are copied run by run, fast enough for a snapshot a frame.
   public class NetJson
   {
      private var s:String;
      private var i:int;

      public static function parse(param1:String) : *
      {
         var p:NetJson = new NetJson();
         p.s = param1;
         p.i = 0;
         var v:* = p.value();
         p.space();
         if(p.i != p.s.length)
         {
            throw new Error("extra text at " + p.i);
         }
         return v;
      }

      public static function quote(param1:String) : String
      {
         var out:String = "\"";
         var start:int = 0;
         for(var k:int = 0; k < param1.length; k++)
         {
            var c:Number = param1.charCodeAt(k);
            if(c == 34 || c == 92 || c < 32)
            {
               out += param1.substring(start,k);
               if(c == 34)
               {
                  out += "\\\"";
               }
               else if(c == 92)
               {
                  out += "\\\\";
               }
               else
               {
                  var h:String = c.toString(16);
                  out += "\\u" + "0000".substr(h.length) + h;
               }
               start = k + 1;
            }
         }
         return out + param1.substring(start) + "\"";
      }

      private function space() : void
      {
         while(i < s.length && " \t\r\n".indexOf(s.charAt(i)) >= 0)
         {
            i++;
         }
      }

      private function value() : *
      {
         space();
         if(i >= s.length)
         {
            throw new Error("unexpected end");
         }
         var c:String = s.charAt(i);
         if(c == "{")
         {
            var o:Object = {};
            i++;
            space();
            if(s.charAt(i) == "}")
            {
               i++;
               return o;
            }
            while(true)
            {
               space();
               if(s.charAt(i) != "\"")
               {
                  throw new Error("expected a key at " + i);
               }
               var key:String = string();
               space();
               if(s.charAt(i) != ":")
               {
                  throw new Error("expected : at " + i);
               }
               i++;
               o[key] = value();
               space();
               if(s.charAt(i) == ",")
               {
                  i++;
                  continue;
               }
               if(s.charAt(i) == "}")
               {
                  i++;
                  return o;
               }
               throw new Error("expected , or } at " + i);
            }
         }
         if(c == "[")
         {
            var a:Array = [];
            i++;
            space();
            if(s.charAt(i) == "]")
            {
               i++;
               return a;
            }
            while(true)
            {
               a.push(value());
               space();
               if(s.charAt(i) == ",")
               {
                  i++;
                  continue;
               }
               if(s.charAt(i) == "]")
               {
                  i++;
                  return a;
               }
               throw new Error("expected , or ] at " + i);
            }
         }
         if(c == "\"")
         {
            return string();
         }
         if(s.substr(i,4) == "true")
         {
            i += 4;
            return true;
         }
         if(s.substr(i,5) == "false")
         {
            i += 5;
            return false;
         }
         if(s.substr(i,4) == "null")
         {
            i += 4;
            return null;
         }
         var start:int = i;
         while(i < s.length && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0)
         {
            i++;
         }
         var n:Number = Number(s.substring(start,i));
         if(i == start || isNaN(n))
         {
            throw new Error("bad value at " + start);
         }
         return n;
      }

      // copies the runs between escapes in one go
      private function string() : String
      {
         var out:String = "";
         i++;
         while(true)
         {
            var q:int = s.indexOf("\"",i);
            if(q < 0)
            {
               throw new Error("unterminated string");
            }
            var b:int = s.indexOf("\\",i);
            if(b < 0 || b > q)
            {
               out += s.substring(i,q);
               i = q + 1;
               return out;
            }
            out += s.substring(i,b);
            var e:String = s.charAt(b + 1);
            i = b + 2;
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
            else if(e == "b")
            {
               out += "\b";
            }
            else if(e == "f")
            {
               out += "\f";
            }
            else if(e == "u")
            {
               out += String.fromCharCode(parseInt(s.substr(i,4),16));
               i += 4;
            }
            else
            {
               out += e;
            }
         }
         return out;
      }
   }
}
