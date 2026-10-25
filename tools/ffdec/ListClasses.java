import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.abc.ABC;
import com.jpexs.decompiler.flash.tags.ABCContainerTag;
import java.io.FileInputStream;
import java.io.InputStream;

/** Debug: prints every class whose name contains the filter, with its index and method count.
 *   java -cp "<ffdec>/lib/*" ListClasses.java file.swf filter */
public class ListClasses {
    public static void main(String[] args) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(args[0])) { swf = new SWF(in, true); }
        for (ABCContainerTag c : swf.getAbcList()) {
            ABC abc = c.getABC();
            for (int i = 0; i < abc.instance_info.size(); i++) {
                String n = abc.instance_info.get(i).getName(abc.constants).getNameWithNamespace(new java.util.HashSet<>(), abc, abc.constants, true).toRawString();
                if (n.contains(args[1])) {
                    System.out.println(i + " " + n + " instTraits=" + abc.instance_info.get(i).instance_traits.traits.size()
                        + " staticTraits=" + abc.class_info.get(i).static_traits.traits.size());
                    if (args.length > 2 && n.equals(args[2])) {
                        for (com.jpexs.decompiler.flash.abc.types.traits.Trait t : abc.class_info.get(i).static_traits.traits) {
                            com.jpexs.decompiler.flash.abc.types.Multiname m = t.getName(abc);
                            System.out.println("   static " + m.getNameWithNamespace(new java.util.HashSet<>(), abc, abc.constants, true).toRawString()
                                + " ns=" + m.getNamespace(abc.constants).getKindStr() + ":" + m.getNamespace(abc.constants).getName(abc.constants).toRawString());
                        }
                    }
                }
            }
            for (int s = 0; s < abc.script_info.size(); s++) {
                String t = abc.script_info.get(s).traits.traits.toString();
                if (t.contains(args[1])) System.out.println("script " + s + " traits " + abc.script_info.get(s).traits.traits.size());
            }
        }
    }
}
