package mynet
{
   // Minimal JSON reader (objects, arrays, strings, numbers, true/false/null), so the build doesn't depend on
   // the player having the built-in JSON class.
   public class NetJson
   {
      private var s:String;
      private var i:int;

      public static function parse(text:String) : *
      {
         var p:NetJson = new NetJson();
         p.s = text;
         p.i = 0;
         var v:* = p.value();
         p.space();
         if(p.i != p.s.length)
         {
            throw new Error("extra text at " + p.i);
         }
         return v;
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
               var k:String = string();
               space();
               if(s.charAt(i) != ":")
               {
                  throw new Error("expected : at " + i);
               }
               i++;
               o[k] = value();
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
         if(s.substr(i, 4) == "true")
         {
            i += 4;
            return true;
         }
         if(s.substr(i, 5) == "false")
         {
            i += 5;
            return false;
         }
         if(s.substr(i, 4) == "null")
         {
            i += 4;
            return null;
         }
         var start:int = i;
         while(i < s.length && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0)
         {
            i++;
         }
         var n:Number = Number(s.substring(start, i));
         if(i == start || isNaN(n))
         {
            throw new Error("bad value at " + start);
         }
         return n;
      }

      private function string() : String
      {
         var out:String = "";
         i++;
         while(i < s.length)
         {
            var c:String = s.charAt(i++);
            if(c == "\"")
            {
               return out;
            }
            if(c != "\\")
            {
               out += c;
               continue;
            }
            var e:String = s.charAt(i++);
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
               out += String.fromCharCode(parseInt(s.substr(i, 4), 16));
               i += 4;
            }
            else
            {
               out += e;
            }
         }
         throw new Error("unterminated string");
      }
   }
}
