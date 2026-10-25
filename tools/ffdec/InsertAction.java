import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.action.Action;
import com.jpexs.decompiler.flash.action.parser.script.ActionScript2Parser;
import com.jpexs.decompiler.flash.tags.DoActionTag;
import com.jpexs.decompiler.flash.tags.ShowFrameTag;
import com.jpexs.decompiler.flash.tags.Tag;

import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

/**
 * Compiles an AS2 source file and adds it as a new DoAction tag at the end of a main-timeline frame.
 * The game's own scripts are left as they are (nothing is decompiled or recompiled).
 *
 *   java -cp "<ffdec>/lib/*" InsertAction.java in.swf out.swf <frame> a.as [b.as ...]
 * Each file becomes its own DoAction tag, in order.
 */
public class InsertAction {
    public static void main(String[] args) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(args[0])) {
            swf = new SWF(in, true);
        }
        int frame = Integer.parseInt(args[2]);
        ShowFrameTag at = null;
        int n = 0;
        for (Tag t : swf.getTags()) {
            if (t instanceof ShowFrameTag && ++n == frame) {
                at = (ShowFrameTag) t;
                break;
            }
        }
        if (at == null) {
            System.err.println("SEVERE: frame " + frame + " not found");
            System.exit(1);
        }
        for (int i = 3; i < args.length; i++) {
            String src = new String(Files.readAllBytes(Paths.get(args[i])), StandardCharsets.UTF_8);
            DoActionTag tag = new DoActionTag(swf);
            List<Action> actions;
            try {
                actions = new ActionScript2Parser(swf, tag).actionsFromString(src, "UTF-8");
            } catch (Exception e) {
                System.err.println("SEVERE: " + args[i] + ": " + e);
                System.exit(1);
                return;
            }
            tag.setActions(actions);
            tag.setModified(true);
            swf.addTag(swf.indexOfTag(at), tag);
            System.out.println(args[i] + ": " + actions.size() + " actions");
        }
        swf.clearAllCache();
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(args[1]))) {
            swf.saveTo(out);
        }
        System.exit(0);
    }
}
