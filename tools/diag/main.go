package main

import (
	"bufio"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf16"
)

const SEC = 2048

var targets = []string{"FONTS_JP.G1N", "FONTS.G1N", "UISTRINGSJPN.INI", "UISTRINGSENG.INI", "LOCALIZEDCOMMONPACKAGE_JPN.CPKG", "LOCALIZEDCOMMONPACKAGE_ENG.CPKG", "SUBTITLE001JPN.INI", "SUBTITLE001ENG.INI", "FONTS", "TROJANMUSOU", "PARAM.SFO"}

func rd(f *os.File, off int64, n int) []byte {
	b := make([]byte, n)
	f.ReadAt(b, off)
	return b
}

func name(b []byte, joliet bool) string {
	if joliet {
		u := make([]uint16, len(b)/2)
		for i := range u {
			u[i] = binary.BigEndian.Uint16(b[2*i:])
		}
		return string(utf16.Decode(u))
	}
	return string(b)
}

func norm(s string) string {
	if i := strings.Index(s, ";"); i >= 0 {
		s = s[:i]
	}
	return strings.ToUpper(strings.TrimSuffix(s, "."))
}

var w *bufio.Writer
var count map[string]int

func walk(f *os.File, lba, size uint32, prefix string, joliet bool, depth int, tree string) {
	if depth > 20 || size > 64*1024*1024 {
		return
	}
	data := rd(f, int64(lba)*SEC, int(size))
	p := 0
	for p < len(data) {
		l := int(data[p])
		if l == 0 {
			p = (p/SEC + 1) * SEC
			continue
		}
		if p+l > len(data) || l < 34 {
			fmt.Fprintf(w, "  !! bad record len %d at dir lba %d off %d (%s)\n", l, lba, p, prefix)
			break
		}
		r := data[p : p+l]
		nl := int(r[32])
		nb := r[33 : 33+nl]
		if !(nl == 1 && (nb[0] == 0 || nb[0] == 1)) {
			nm := name(nb, joliet)
			full := prefix + nm
			count[tree]++
			le := binary.LittleEndian.Uint32(r[2:])
			be := binary.BigEndian.Uint32(r[6:])
			sl := binary.LittleEndian.Uint32(r[10:])
			sb := binary.BigEndian.Uint32(r[14:])
			for _, t := range targets {
				if norm(nm) == t {
					fmt.Fprintf(w, "[%s] %s\n    rawname=%s recoff=%d lbaLE=%d lbaBE=%d sizeLE=%d sizeBE=%d flags=%02x extattr=%d ilv=%d/%d\n",
						tree, full, hex.EncodeToString(nb), int64(lba)*SEC+int64(p), le, be, sl, sb, r[25], r[1], r[26], r[27])
				}
			}
			if r[25]&2 != 0 {
				walk(f, le, sl, full+"/", joliet, depth+1, tree)
			}
		}
		p += l
	}
}

func main() {
	src := ""
	if len(os.Args) > 1 {
		src = os.Args[1]
	} else {
		fmt.Print("ISO 파일을 끌어다 놓고 Enter:\n> ")
		s, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		src = strings.Trim(strings.TrimSpace(s), "\"' ")
	}
	f, err := os.Open(src)
	if err != nil {
		fmt.Println("열 수 없음:", err)
		return
	}
	out := strings.TrimSuffix(src, filepath.Ext(src)) + "_diag.txt"
	of, _ := os.Create(out)
	w = bufio.NewWriter(of)
	count = map[string]int{}
	st, _ := f.Stat()
	fmt.Fprintf(w, "file %s size %d sectors %d\n", src, st.Size(), st.Size()/SEC)
	s0 := rd(f, 0, 64)
	fmt.Fprintf(w, "sector0 %s\n", hex.EncodeToString(s0))
	n := binary.BigEndian.Uint32(s0)
	if n > 0 && n < 128 {
		tb := rd(f, 8, int(n)*8)
		fmt.Fprintf(w, "regions(%d): ", n)
		for i := 0; i < int(n)*2; i++ {
			fmt.Fprintf(w, "%d ", binary.BigEndian.Uint32(tb[i*4:]))
		}
		fmt.Fprintln(w)
	}
	s1 := rd(f, 0xF70, 16)
	fmt.Fprintf(w, "0xF70: %q\n", s1)
	for s := int64(16); s < 40; s++ {
		vd := rd(f, s*SEC, SEC)
		if string(vd[1:6]) != "CD001" {
			fmt.Fprintf(w, "sector %d: not CD001 (%q)\n", s, vd[0:8])
			continue
		}
		t := vd[0]
		fmt.Fprintf(w, "VD sector %d type %d esc=%q volsizeLE=%d volsizeBE=%d ptsize=%d ptL=%d ptM=%d\n", s, t, vd[88:91],
			binary.LittleEndian.Uint32(vd[80:]), binary.BigEndian.Uint32(vd[84:]), binary.LittleEndian.Uint32(vd[132:]),
			binary.LittleEndian.Uint32(vd[140:]), binary.BigEndian.Uint32(vd[148:]))
		if t == 255 {
			break
		}
		if t == 1 || t == 2 {
			j := t == 2 && vd[88] == '%'
			tree := fmt.Sprintf("type%d-sector%d", t, s)
			root := vd[156:190]
			walk(f, binary.LittleEndian.Uint32(root[2:]), binary.LittleEndian.Uint32(root[10:]), "", j, 0, tree)
		}
	}
	// UDF probe
	for s := int64(16); s < 32; s++ {
		b := rd(f, s*SEC, 8)
		fmt.Fprintf(w, "sector %d head %q\n", s, b)
	}
	for _, s := range []int64{256, st.Size()/SEC - 1, st.Size()/SEC - 257} {
		b := rd(f, s*SEC, 32)
		fmt.Fprintf(w, "sector %d tag=%d ver=%d loc=%d raw=%s\n", s, binary.LittleEndian.Uint16(b[0:]), binary.LittleEndian.Uint16(b[2:]), binary.LittleEndian.Uint32(b[12:]), hex.EncodeToString(b))
	}
	udf(f)
	for k, v := range count {
		fmt.Fprintf(w, "tree %s entries %d\n", k, v)
	}
	w.Flush()
	of.Close()
	fmt.Println("완료:", out)
	fmt.Print("Enter 키를 누르면 종료합니다...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func tagAt(f *os.File, sec int64) (uint16, []byte) {
	b := rd(f, sec*SEC, SEC)
	return binary.LittleEndian.Uint16(b[0:]), b
}

func udf(f *os.File) {
	id, a := tagAt(f, 256)
	if id != 2 {
		fmt.Fprintln(w, "UDF: no anchor at 256")
		return
	}
	mlen := binary.LittleEndian.Uint32(a[16:])
	mloc := binary.LittleEndian.Uint32(a[20:])
	fmt.Fprintf(w, "UDF anchor: main VDS loc %d len %d\n", mloc, mlen)
	var pstart uint32
	var fsdLoc uint32
	var fsdPart uint16
	for i := uint32(0); i < mlen/SEC; i++ {
		t, b := tagAt(f, int64(mloc+i))
		switch t {
		case 1:
			fmt.Fprintf(w, "  PVD\n")
		case 5:
			pnum := binary.LittleEndian.Uint16(b[22:])
			pstart = binary.LittleEndian.Uint32(b[188:])
			plen := binary.LittleEndian.Uint32(b[192:])
			fmt.Fprintf(w, "  PartitionDesc num %d start %d len %d contents %q\n", pnum, pstart, plen, b[25:48])
		case 6:
			fsdLoc = binary.LittleEndian.Uint32(b[248+4:])
			fsdPart = binary.LittleEndian.Uint16(b[248+8:])
			nmaps := binary.LittleEndian.Uint32(b[268:])
			mtl := binary.LittleEndian.Uint32(b[264:])
			fmt.Fprintf(w, "  LVD domain %q fsd lb %d part %d maps %d maptablelen %d maps=%s\n", b[416+1:416+24], fsdLoc, fsdPart, nmaps, mtl, hex.EncodeToString(b[440:440+mtl]))
		case 8:
			fmt.Fprintf(w, "  Terminator\n")
			i = mlen
		default:
			fmt.Fprintf(w, "  tag %d\n", t)
		}
	}
	t, fsd := tagAt(f, int64(pstart+fsdLoc))
	fmt.Fprintf(w, "FSD tag %d\n", t)
	if t != 256 {
		return
	}
	rootLoc := binary.LittleEndian.Uint32(fsd[400+4:])
	fmt.Fprintf(w, "root ICB lb %d\n", rootLoc)
	udfWalk(f, pstart, rootLoc, "", 0)
}

func udfWalk(f *os.File, pstart, lb uint32, prefix string, depth int) {
	if depth > 12 {
		return
	}
	t, fe := tagAt(f, int64(pstart+lb))
	var l_ea, l_ad uint32
	var off int
	var info uint64
	switch t {
	case 261:
		info = binary.LittleEndian.Uint64(fe[56:])
		l_ea = binary.LittleEndian.Uint32(fe[168:])
		l_ad = binary.LittleEndian.Uint32(fe[172:])
		off = 176
	case 266:
		info = binary.LittleEndian.Uint64(fe[56:])
		l_ea = binary.LittleEndian.Uint32(fe[208:])
		l_ad = binary.LittleEndian.Uint32(fe[212:])
		off = 216
	default:
		fmt.Fprintf(w, "  ?? tag %d at lb %d (%s)\n", t, lb, prefix)
		return
	}
	adtype := binary.LittleEndian.Uint16(fe[16+18:]) & 7
	ads := fe[off+int(l_ea) : off+int(l_ea)+int(l_ad)]
	ftype := fe[16+11]
	if ftype != 4 {
		return
	}
	// read directory data
	var data []byte
	for p := 0; p+8 <= len(ads); {
		ln := binary.LittleEndian.Uint32(ads[p:]) & 0x3fffffff
		pos := binary.LittleEndian.Uint32(ads[p+4:])
		data = append(data, rd(f, int64(pstart+pos)*SEC, int(ln))...)
		if adtype == 0 {
			p += 8
		} else {
			p += 16
		}
	}
	if adtype == 3 {
		data = ads
	}
	_ = info
	for p := 0; p+38 <= len(data); {
		ch := data[p+18]
		lfi := int(data[p+19])
		icb := binary.LittleEndian.Uint32(data[p+20+4:])
		liu := int(binary.LittleEndian.Uint16(data[p+36:]))
		nb := data[p+38+liu : p+38+liu+lfi]
		nm := ""
		if lfi > 0 {
			if nb[0] == 8 {
				nm = string(nb[1:])
			} else {
				u := make([]uint16, (lfi-1)/2)
				for i := range u {
					u[i] = binary.BigEndian.Uint16(nb[1+2*i:])
				}
				nm = string(utf16.Decode(u))
			}
		}
		rl := (38 + liu + lfi + 3) &^ 3
		p += rl
		if ch&8 != 0 || lfi == 0 {
			continue
		}
		full := prefix + nm
		if ch&2 != 0 {
			udfWalk(f, pstart, icb, full+"/", depth+1)
			continue
		}
		for _, tg := range targets {
			if strings.ToUpper(nm) == tg {
				t2, e := tagAt(f, int64(pstart+icb))
				var inf uint64
				var la, lad uint32
				o := 176
				if t2 == 266 {
					inf = binary.LittleEndian.Uint64(e[56:])
					la = binary.LittleEndian.Uint32(e[208:])
					lad = binary.LittleEndian.Uint32(e[212:])
					o = 216
				} else {
					inf = binary.LittleEndian.Uint64(e[56:])
					la = binary.LittleEndian.Uint32(e[168:])
					lad = binary.LittleEndian.Uint32(e[172:])
				}
				at := binary.LittleEndian.Uint16(e[16+18:]) & 7
				ad := e[o+int(la) : o+int(la)+int(lad)]
				fmt.Fprintf(w, "[UDF] %s fe lb %d tag %d infolen %d adtype %d ads=%s\n", full, icb, t2, inf, at, hex.EncodeToString(ad))
			}
		}
	}
}
