import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.tags.SymbolClassTag;
import com.jpexs.decompiler.flash.tags.Tag;

import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Makes another class the document class (character 0 in SymbolClass).
 *
 *   java -cp "<ffdec>/lib/*" SetDocClass.java in.swf out.swf pkg.NewDocClass
 *
 * Prints the old document class. Run 2 uses it so the mod's subclass of the game's main class is what the
 * player builds; the game's own classes are never recompiled.
 */
public class SetDocClass {
    public static void main(String[] args) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(args[0])) {
            swf = new SWF(in, true);
        }
        int changed = 0;
        for (Tag t : swf.getTags()) {
            if (t instanceof SymbolClassTag) {
                SymbolClassTag s = (SymbolClassTag) t;
                for (int i = 0; i < s.tags.size(); i++) {
                    if (s.tags.get(i) == 0) {
                        System.out.println("old document class: " + s.names.get(i));
                        s.names.set(i, args[2]);
                        s.setModified(true);
                        changed++;
                    }
                }
            }
        }
        if (changed != 1) {
            System.out.println("SEVERE: expected one document class entry, found " + changed);
            System.exit(1);
        }
        swf.clearAllCache();
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(args[1]))) {
            swf.saveTo(out);
        }
        System.out.println("document class: " + args[2]);
    }
}
