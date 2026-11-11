import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.tags.DefineSpriteTag;
import com.jpexs.decompiler.flash.tags.Tag;

import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Re-encodes a SWF at another version. Every tag is written again, so clip-event flags take the new version's size
 * (16 bits in SWF 5, 32 bits from SWF 6). Only changing the header byte would misread every onClipEvent.
 *
 *   java -cp "<ffdec>/lib/*" SetVersion.java in.swf out.swf 6
 */
public class SetVersion {
    static int marked = 0;

    static void mark(Iterable<Tag> tags) {
        for (Tag t : tags) {
            t.setModified(true);
            marked++;
            if (t instanceof DefineSpriteTag) {
                mark(((DefineSpriteTag) t).getTags());
            }
        }
    }

    public static void main(String[] args) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(args[0])) {
            swf = new SWF(in, true);
        }
        swf.version = Integer.parseInt(args[2]);
        mark(swf.getTags());
        swf.setModified(true);
        swf.clearAllCache();
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(args[1]))) {
            swf.saveTo(out);
        }
        System.out.println("version " + swf.version + ", " + marked + " tags rewritten");
        System.exit(0);
    }
}
