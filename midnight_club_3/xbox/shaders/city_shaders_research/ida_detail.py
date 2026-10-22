for vt in [0x635C18, 0x635BB8]:
    emit('VT %#x' % vt)
    for i in range(16):
        fn = idc.get_wide_dword(vt+4*i)
        emit('%d %#x %s' % (i, fn, idc.get_func_name(fn)))
    fn = idc.get_wide_dword(vt+40)
    try: emit(ida_hexrays.decompile(fn))
    except Exception as e: emit(e)
for ea in [0x2AFCD8,0x2AFE40,0x2B5B58,0x596F40,0x2628F8]:
    emit('FUNCTION %#x' % ea)
    try: emit(ida_hexrays.decompile(ea))
    except Exception as e: emit(e)
for ea in [0x2626D8,0x262960,0x262A60,0x2628F8]:
    f=ida_funcs.get_func(ea)
    if f:
        emit('DISASM %#x' % ea)
        for addr in idautils.FuncItems(ea): emit('%08x %s' % (addr,idc.GetDisasm(addr)))
