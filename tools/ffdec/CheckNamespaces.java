import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.abc.ABC;
import com.jpexs.decompiler.flash.abc.avm2.AVM2ConstantPool;
import com.jpexs.decompiler.flash.abc.types.InstanceInfo;
import com.jpexs.decompiler.flash.abc.types.Multiname;
import com.jpexs.decompiler.flash.tags.ABCContainerTag;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Guard against the protected-namespace break (MODLOG gotcha 5).
 *
 * The obfuscator renamed each game class's protected namespace. When FFDec
 * recompiles a class from source it gives the class a differently named
 * protected namespace, and every game subclass that was NOT recompiled then
 * fails at runtime (#1070 "Method <ns>::foo not found").
 *
 *   java -cp "<ffdec>/lib/*" CheckNamespaces.java original.swf patched.swf
 *
 * Lists every class whose protected namespace changed and fails (exit 1) when
 * such a class has a subclass whose protected namespace did not change too.
 */
public class CheckNamespaces {
    static class Cls {
        String name;
        String superName;
        String protectedNs;
    }

    static Map<String, Cls> load(String path) throws Exception {
        SWF swf;
        try (InputStream in = new FileInputStream(path)) {
            swf = new SWF(in, true);
        }
        Map<String, Cls> out = new LinkedHashMap<>();
        for (ABCContainerTag c : swf.getAbcList()) {
            ABC abc = c.getABC();
            AVM2ConstantPool cp = abc.constants;
            for (InstanceInfo ii : abc.instance_info) {
                Cls k = new Cls();
                k.name = qname(abc, cp, ii.name_index);
                k.superName = ii.super_index > 0 ? qname(abc, cp, ii.super_index) : "";
                k.protectedNs = ii.protectedNS > 0
                        ? String.valueOf(cp.getNamespace(ii.protectedNS).getName(cp).toRawString()) : "";
                out.put(k.name, k);
            }
        }
        return out;
    }

    static String qname(ABC abc, AVM2ConstantPool cp, int index) {
        Multiname m = cp.getMultiname(index);
        return m.getNameWithNamespace(new HashSet<>(), abc, cp, true).toRawString();
    }

    public static void main(String[] args) throws Exception {
        Map<String, Cls> before = load(args[0]);
        Map<String, Cls> after = load(args[1]);
        List<String> changed = new ArrayList<>();
        for (Cls k : after.values()) {
            Cls o = before.get(k.name);
            if (o != null && !o.protectedNs.equals(k.protectedNs)) {
                changed.add(k.name);
                System.out.println("recompiled: " + k.name + "  protected ns '" + o.protectedNs + "' -> '" + k.protectedNs + "'");
            }
        }
        int broken = 0;
        for (Cls k : after.values()) {
            if (changed.contains(k.superName) && !changed.contains(k.name) && before.containsKey(k.name)) {
                System.out.println("BROKEN: " + k.name + " extends recompiled " + k.superName
                        + " but was not recompiled; its super calls to protected members will fail");
                broken++;
            }
        }
        System.out.println(changed.size() + " recompiled game classes, " + broken + " broken subclasses");
        System.exit(broken > 0 ? 1 : 0);
    }
}
