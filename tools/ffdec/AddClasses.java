import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.abc.avm2.parser.script.ActionScript3Parser;
import com.jpexs.decompiler.flash.tags.ABCContainerTag;
import com.jpexs.decompiler.flash.tags.Tag;

import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Adds empty public classes to an AS3 SWF, the way FFDec's GUI "Add class" does
 * (ffdec -importScript can only replace classes that already exist).
 * build.py runs this first, then -importScript fills the stubs with real code.
 *
 *   java -cp "<ffdec>/lib/*" AddClasses.java in.swf out.swf pkg.Name [pkg.Name2 ...]
 *
 * Stubs go into the game's own ABC tag (the one holding the document class), so
 * the new classes and the game resolve each other without verify error 1014.
 */
public class AddClasses {
    public static void main(String[] args) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(args[0])) {
            swf = new SWF(in, true);
        }
        String doc = swf.getDocumentClass();
        ABCContainerTag target = null;
        for (ABCContainerTag c : swf.getAbcList()) {
            if (target == null || c.getABC().findClassByName(doc) >= 0) {
                target = c;
            }
        }
        for (int i = 2; i < args.length; i++) {
            String fq = args[i];
            int dot = fq.lastIndexOf('.');
            String pkg = dot < 0 ? "" : fq.substring(0, dot);
            String name = fq.substring(dot + 1);
            if (target.getABC().findClassByName(fq) >= 0) {
                System.out.println("exists: " + fq);
                continue;
            }
            String src = "package " + pkg + " {public class " + name + " { }}";
            swf.getAbcIndex().selectAbc(target.getABC());
            new ActionScript3Parser(swf.getAbcIndex()).addScript(src, fq.replace('.', '/'), 0, 0, doc, target.getABC());
            System.out.println("added: " + fq);
        }
        ((Tag) target).setModified(true);
        swf.clearAllCache();
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(args[1]))) {
            swf.saveTo(out);
        }
        System.exit(0);
    }
}
