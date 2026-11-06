"""mc3_xbe: read MC3's Xbox default.xbe by virtual address. The library the mc3_xbe_* tools share.

Works on the file itself (no conversion step): the XBE header, its sections at their virtual addresses, the
kernel import table (retail or debug keys), C strings, and names for addresses.

Environment variables this library reads (set them, do not edit the code):
    MC3_XBOX_XBE      the game's default.xbe (Midnight Club 3: DUB Edition Remix, Xbox; title id 54540079)
    MC3_XBOX_NAMES    optional: name files to use, separated by the system path separator (';' on Windows).
                      Each line is "<hex address> <name> [anything]"; '#' starts a comment; a folder means
                      every .txt/.tsv in it. Without it, the mc3_xbox_names data package of this repository
                      is used when it is there. Earlier files win over later ones.

Use from a tool:
    import mc3_xbe
    xbe = mc3_xbe.open_xbe()            # MC3_XBOX_XBE, or a path
    xbe.read(0x2c9aa0, 16); xbe.u32(0x4a4914); xbe.name(0x35da80); xbe.cstring(0x473490)

Origin: the MC3 Xbox C++ decompilation's tools (xbe2pe.py, xdis.py), written for mc_research by SaltySasha.
The kernel export names follow Cxbx-Reloaded's KernelThunk.cpp ordinals.
"""
import bisect
import os
import pathlib
import re
import struct

RETAIL_ENTRY_KEY, RETAIL_THUNK_KEY = 0xA8FC57AB, 0x5B6D40B6
DEBUG_ENTRY_KEY, DEBUG_THUNK_KEY = 0x94859D4B, 0xEFB1F152
SECTION_EXECUTABLE = 0x4

# xboxkrnl.exe exports by ordinal.
KERNEL_EXPORTS = {
    1: 'AvGetSavedDataAddress', 2: 'AvSendTVEncoderOption', 3: 'AvSetDisplayMode', 4: 'AvSetSavedDataAddress',
    5: 'DbgBreakPoint', 6: 'DbgBreakPointWithStatus', 7: 'DbgLoadImageSymbols', 8: 'DbgPrint',
    9: 'HalReadSMCTrayState', 10: 'DbgPrompt', 11: 'DbgUnLoadImageSymbols', 12: 'ExAcquireReadWriteLockExclusive',
    13: 'ExAcquireReadWriteLockShared', 14: 'ExAllocatePool', 15: 'ExAllocatePoolWithTag', 16: 'ExEventObjectType',
    17: 'ExFreePool', 18: 'ExInitializeReadWriteLock', 19: 'ExInterlockedAddLargeInteger',
    20: 'ExInterlockedAddLargeStatistic', 21: 'ExInterlockedCompareExchange64', 22: 'ExMutantObjectType',
    23: 'ExQueryPoolBlockSize', 24: 'ExQueryNonVolatileSetting', 25: 'ExReadWriteRefurbInfo', 26: 'ExRaiseException',
    27: 'ExRaiseStatus', 28: 'ExReleaseReadWriteLock', 29: 'ExSaveNonVolatileSetting', 30: 'ExSemaphoreObjectType',
    31: 'ExTimerObjectType', 32: 'ExfInterlockedInsertHeadList', 33: 'ExfInterlockedInsertTailList',
    34: 'ExfInterlockedRemoveHeadList', 35: 'FscGetCacheSize', 36: 'FscInvalidateIdleBlocks', 37: 'FscSetCacheSize',
    38: 'HalClearSoftwareInterrupt', 39: 'HalDisableSystemInterrupt', 40: 'HalDiskCachePartitionCount',
    41: 'HalDiskModelNumber', 42: 'HalDiskSerialNumber', 43: 'HalEnableSystemInterrupt', 44: 'HalGetInterruptVector',
    45: 'HalReadSMBusValue', 46: 'HalReadWritePCISpace', 47: 'HalRegisterShutdownNotification',
    48: 'HalRequestSoftwareInterrupt', 49: 'HalReturnToFirmware', 50: 'HalWriteSMBusValue', 59: 'IoAllocateIrp',
    60: 'IoBuildAsynchronousFsdRequest', 61: 'IoBuildDeviceIoControlRequest', 62: 'IoBuildSynchronousFsdRequest',
    63: 'IoCheckShareAccess', 64: 'IoCompletionObjectType', 65: 'IoCreateDevice', 66: 'IoCreateFile',
    67: 'IoCreateSymbolicLink', 68: 'IoDeleteDevice', 69: 'IoDeleteSymbolicLink', 70: 'IoDeviceObjectType',
    71: 'IoFileObjectType', 72: 'IoFreeIrp', 73: 'IoInitializeIrp', 74: 'IoInvalidDeviceRequest',
    75: 'IoQueryFileInformation', 76: 'IoQueryVolumeInformation', 77: 'IoQueueThreadIrp', 78: 'IoRemoveShareAccess',
    79: 'IoSetIoCompletion', 80: 'IoSetShareAccess', 81: 'IoStartNextPacket', 82: 'IoStartNextPacketByKey',
    83: 'IoStartPacket', 84: 'IoSynchronousDeviceIoControlRequest', 85: 'IoSynchronousFsdRequest',
    86: 'IofCallDriver', 87: 'IofCompleteRequest', 88: 'KdDebuggerEnabled', 89: 'KdDebuggerNotPresent',
    90: 'IoDismountVolume', 91: 'IoDismountVolumeByName', 92: 'KeAlertResumeThread', 93: 'KeAlertThread',
    94: 'KeBoostPriorityThread', 95: 'KeBugCheck', 96: 'KeBugCheckEx', 97: 'KeCancelTimer', 98: 'KeConnectInterrupt',
    99: 'KeDelayExecutionThread', 100: 'KeDisconnectInterrupt', 101: 'KeEnterCriticalRegion', 102: 'MmGlobalData',
    103: 'KeGetCurrentIrql', 104: 'KeGetCurrentThread', 105: 'KeInitializeApc', 106: 'KeInitializeDeviceQueue',
    107: 'KeInitializeDpc', 108: 'KeInitializeEvent', 109: 'KeInitializeInterrupt', 110: 'KeInitializeMutant',
    111: 'KeInitializeQueue', 112: 'KeInitializeSemaphore', 113: 'KeInitializeTimerEx',
    114: 'KeInsertByKeyDeviceQueue', 115: 'KeInsertDeviceQueue', 116: 'KeInsertHeadQueue', 117: 'KeInsertQueue',
    118: 'KeInsertQueueApc', 119: 'KeInsertQueueDpc', 120: 'KeInterruptTime', 121: 'KeIsExecutingDpc',
    122: 'KeLeaveCriticalRegion', 123: 'KePulseEvent', 124: 'KeQueryBasePriorityThread', 125: 'KeQueryInterruptTime',
    126: 'KeQueryPerformanceCounter', 127: 'KeQueryPerformanceFrequency', 128: 'KeQuerySystemTime',
    129: 'KeRaiseIrqlToDpcLevel', 130: 'KeRaiseIrqlToSynchLevel', 131: 'KeReleaseMutant', 132: 'KeReleaseSemaphore',
    133: 'KeRemoveByKeyDeviceQueue', 134: 'KeRemoveDeviceQueue', 135: 'KeRemoveEntryDeviceQueue',
    136: 'KeRemoveQueue', 137: 'KeRemoveQueueDpc', 138: 'KeResetEvent', 139: 'KeRestoreFloatingPointState',
    140: 'KeResumeThread', 141: 'KeRundownQueue', 142: 'KeSaveFloatingPointState', 143: 'KeSetBasePriorityThread',
    144: 'KeSetDisableBoostThread', 145: 'KeSetEvent', 146: 'KeSetEventBoostPriority', 147: 'KeSetPriorityProcess',
    148: 'KeSetPriorityThread', 149: 'KeSetTimer', 150: 'KeSetTimerEx', 151: 'KeStallExecutionProcessor',
    152: 'KeSuspendThread', 153: 'KeSynchronizeExecution', 154: 'KeSystemTime', 155: 'KeTestAlertThread',
    156: 'KeTickCount', 157: 'KeTimeIncrement', 158: 'KeWaitForMultipleObjects', 159: 'KeWaitForSingleObject',
    160: 'KfRaiseIrql', 161: 'KfLowerIrql', 162: 'KiBugCheckData', 163: 'KiUnlockDispatcherDatabase',
    164: 'LaunchDataPage', 165: 'MmAllocateContiguousMemory', 166: 'MmAllocateContiguousMemoryEx',
    167: 'MmAllocateSystemMemory', 168: 'MmClaimGpuInstanceMemory', 169: 'MmCreateKernelStack',
    170: 'MmDeleteKernelStack', 171: 'MmFreeContiguousMemory', 172: 'MmFreeSystemMemory',
    173: 'MmGetPhysicalAddress', 174: 'MmIsAddressValid', 175: 'MmLockUnlockBufferPages',
    176: 'MmLockUnlockPhysicalPage', 177: 'MmMapIoSpace', 178: 'MmPersistContiguousMemory',
    179: 'MmQueryAddressProtect', 180: 'MmQueryAllocationSize', 181: 'MmQueryStatistics', 182: 'MmSetAddressProtect',
    183: 'MmUnmapIoSpace', 184: 'NtAllocateVirtualMemory', 185: 'NtCancelTimer', 186: 'NtClearEvent', 187: 'NtClose',
    188: 'NtCreateDirectoryObject', 189: 'NtCreateEvent', 190: 'NtCreateFile', 191: 'NtCreateIoCompletion',
    192: 'NtCreateMutant', 193: 'NtCreateSemaphore', 194: 'NtCreateTimer', 195: 'NtDeleteFile',
    196: 'NtDeviceIoControlFile', 197: 'NtDuplicateObject', 198: 'NtFlushBuffersFile', 199: 'NtFreeVirtualMemory',
    200: 'NtFsControlFile', 201: 'NtOpenDirectoryObject', 202: 'NtOpenFile', 203: 'NtOpenSymbolicLinkObject',
    204: 'NtProtectVirtualMemory', 205: 'NtPulseEvent', 206: 'NtQueueApcThread', 207: 'NtQueryDirectoryFile',
    208: 'NtQueryDirectoryObject', 209: 'NtQueryEvent', 210: 'NtQueryFullAttributesFile',
    211: 'NtQueryInformationFile', 212: 'NtQueryIoCompletion', 213: 'NtQueryMutant', 214: 'NtQuerySemaphore',
    215: 'NtQuerySymbolicLinkObject', 216: 'NtQueryTimer', 217: 'NtQueryVirtualMemory',
    218: 'NtQueryVolumeInformationFile', 219: 'NtReadFile', 220: 'NtReadFileScatter', 221: 'NtReleaseMutant',
    222: 'NtReleaseSemaphore', 223: 'NtRemoveIoCompletion', 224: 'NtResumeThread', 225: 'NtSetEvent',
    226: 'NtSetInformationFile', 227: 'NtSetIoCompletion', 228: 'NtSetSystemTime', 229: 'NtSetTimerEx',
    230: 'NtSignalAndWaitForSingleObjectEx', 231: 'NtSuspendThread', 232: 'NtUserIoApcDispatcher',
    233: 'NtWaitForSingleObject', 234: 'NtWaitForSingleObjectEx', 235: 'NtWaitForMultipleObjectsEx',
    236: 'NtWriteFile', 237: 'NtWriteFileGather', 238: 'NtYieldExecution', 239: 'ObCreateObject',
    240: 'ObDirectoryObjectType', 241: 'ObInsertObject', 242: 'ObMakeTemporaryObject', 243: 'ObOpenObjectByName',
    244: 'ObOpenObjectByPointer', 245: 'ObpObjectHandleTable', 246: 'ObReferenceObjectByHandle',
    247: 'ObReferenceObjectByName', 248: 'ObReferenceObjectByPointer', 249: 'ObSymbolicLinkObjectType',
    250: 'ObfDereferenceObject', 251: 'ObfReferenceObject', 252: 'PhyGetLinkState', 253: 'PhyInitialize',
    254: 'PsCreateSystemThread', 255: 'PsCreateSystemThreadEx', 256: 'PsQueryStatistics',
    257: 'PsSetCreateThreadNotifyRoutine', 258: 'PsTerminateSystemThread', 259: 'PsThreadObjectType',
    260: 'RtlAnsiStringToUnicodeString', 261: 'RtlAppendStringToString', 262: 'RtlAppendUnicodeStringToString',
    263: 'RtlAppendUnicodeToString', 264: 'RtlAssert', 265: 'RtlCaptureContext', 266: 'RtlCaptureStackBackTrace',
    267: 'RtlCharToInteger', 268: 'RtlCompareMemory', 269: 'RtlCompareMemoryUlong', 270: 'RtlCompareString',
    271: 'RtlCompareUnicodeString', 272: 'RtlCopyString', 273: 'RtlCopyUnicodeString', 274: 'RtlCreateUnicodeString',
    275: 'RtlDowncaseUnicodeChar', 276: 'RtlDowncaseUnicodeString', 277: 'RtlEnterCriticalSection',
    278: 'RtlEnterCriticalSectionAndRegion', 279: 'RtlEqualString', 280: 'RtlEqualUnicodeString',
    281: 'RtlExtendedIntegerMultiply', 282: 'RtlExtendedLargeIntegerDivide', 283: 'RtlExtendedMagicDivide',
    284: 'RtlFillMemory', 285: 'RtlFillMemoryUlong', 286: 'RtlFreeAnsiString', 287: 'RtlFreeUnicodeString',
    288: 'RtlGetCallersAddress', 289: 'RtlInitAnsiString', 290: 'RtlInitUnicodeString',
    291: 'RtlInitializeCriticalSection', 292: 'RtlIntegerToChar', 293: 'RtlIntegerToUnicodeString',
    294: 'RtlLeaveCriticalSection', 295: 'RtlLeaveCriticalSectionAndRegion', 296: 'RtlLowerChar',
    297: 'RtlMapGenericMask', 298: 'RtlMoveMemory', 299: 'RtlMultiByteToUnicodeN', 300: 'RtlMultiByteToUnicodeSize',
    301: 'RtlNtStatusToDosError', 302: 'RtlRaiseException', 303: 'RtlRaiseStatus', 304: 'RtlTimeFieldsToTime',
    305: 'RtlTimeToTimeFields', 306: 'RtlTryEnterCriticalSection', 307: 'RtlUlongByteSwap',
    308: 'RtlUnicodeStringToAnsiString', 309: 'RtlUnicodeStringToInteger', 310: 'RtlUnicodeToMultiByteN',
    311: 'RtlUnicodeToMultiByteSize', 312: 'RtlUnwind', 313: 'RtlUpcaseUnicodeChar', 314: 'RtlUpcaseUnicodeString',
    315: 'RtlUpcaseUnicodeToMultiByteN', 316: 'RtlUpperChar', 317: 'RtlUpperString', 318: 'RtlUshortByteSwap',
    319: 'RtlWalkFrameChain', 320: 'RtlZeroMemory', 321: 'XboxEEPROMKey', 322: 'XboxHardwareInfo', 323: 'XboxHDKey',
    324: 'XboxKrnlVersion', 325: 'XboxSignatureKey', 326: 'XeImageFileName', 327: 'XeLoadSection',
    328: 'XeUnloadSection', 329: 'READ_PORT_BUFFER_UCHAR', 330: 'READ_PORT_BUFFER_USHORT',
    331: 'READ_PORT_BUFFER_ULONG', 332: 'WRITE_PORT_BUFFER_UCHAR', 333: 'WRITE_PORT_BUFFER_USHORT',
    334: 'WRITE_PORT_BUFFER_ULONG', 335: 'XcSHAInit', 336: 'XcSHAUpdate', 337: 'XcSHAFinal', 338: 'XcRC4Key',
    339: 'XcRC4Crypt', 340: 'XcHMAC', 341: 'XcPKEncPublic', 342: 'XcPKDecPrivate', 343: 'XcPKGetKeyLen',
    344: 'XcVerifyPKCS1Signature', 345: 'XcModExp', 346: 'XcDESKeyParity', 347: 'XcKeyTable', 348: 'XcBlockCrypt',
    349: 'XcBlockCryptCBC', 350: 'XcCryptService', 351: 'XcUpdateCrypto', 352: 'RtlRip', 353: 'XboxLANKey',
    354: 'XboxAlternateSignatureKeys', 355: 'XePublicKeyData', 356: 'HalBootSMCVideoMode', 357: 'IdexChannelObject',
    358: 'HalIsResetOrShutdownPending', 359: 'IoMarkIrpMustComplete', 360: 'HalInitiateShutdown', 361: 'RtlSnprintf',
    362: 'RtlSprintf', 363: 'RtlVsnprintf', 364: 'RtlVsprintf', 365: 'HalEnableSecureTrayEject',
    366: 'HalWriteSMCScratchRegister', 367: 'UnknownAPI367', 368: 'UnknownAPI368', 369: 'UnknownAPI369',
    370: 'XProfpControl', 371: 'XProfpGetData', 372: 'IrtClientInitFast', 373: 'IrtSweep',
    374: 'MmDbgAllocateMemory', 375: 'MmDbgFreeMemory', 376: 'MmDbgQueryAvailablePages', 377: 'MmDbgReleaseAddress',
    378: 'MmDbgWriteCheck',
}


class Xbe:
    """An XBE file, addressed by virtual address."""

    def __init__(self, path):
        self.path = str(path)
        self.d = pathlib.Path(path).read_bytes()
        if self.d[:4] != b'XBEH':
            raise ValueError(f'{path}: not an XBE')
        self.base = self._u32(0x104)
        self.headers_size = self._u32(0x108)
        self.image_size = self._u32(0x10c)
        end = self.base + self.image_size
        ep, th = self._u32(0x128), self._u32(0x158)
        for kind, ek, tk in (('retail', RETAIL_ENTRY_KEY, RETAIL_THUNK_KEY),
                             ('debug', DEBUG_ENTRY_KEY, DEBUG_THUNK_KEY)):
            if self.base <= ep ^ ek < end and self.base <= th ^ tk < end:
                self.kind, self.entry, self.thunk = kind, ep ^ ek, th ^ tk
                break
        else:
            raise ValueError(f'{path}: cannot decode the entry point and kernel thunk address')
        self.sections = []
        for i in range(self._u32(0x11c)):
            o = self._u32(0x120) - self.base + i * 56
            flags, va, vsz, raw, rsz, name_addr = struct.unpack_from('<IIIIII', self.d, o)
            n = name_addr - self.base
            name = self.d[n:self.d.index(0, n)].decode('latin1')
            self.sections.append(dict(name=name, flags=flags, va=va, vsz=vsz, raw=raw, rsz=rsz))
        self.imports = {}
        for i in range(400):
            v = self.u32(self.thunk + 4 * i)
            if v == 0:
                break
            ordinal = v & 0x7fffffff
            self.imports[self.thunk + 4 * i] = KERNEL_EXPORTS.get(ordinal, f'kernel_{ordinal}')
        self._names = None

    def _u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0]

    # ----- memory
    def section_of(self, va):
        for s in self.sections:
            if s['va'] <= va < s['va'] + s['vsz']:
                return s
        return None

    def read(self, va, n):
        """n bytes at va (zeros past a section's file data, as the loader maps it)."""
        out = bytearray()
        while n > 0:
            if self.base <= va < self.base + self.headers_size:
                take = min(n, self.base + self.headers_size - va)
                out += self.d[va - self.base:va - self.base + take]
            else:
                s = self.section_of(va)
                if s is None:
                    raise ValueError(f'{va:#x} is not in the image')
                take = min(n, s['va'] + s['vsz'] - va)
                o = va - s['va']
                chunk = self.d[s['raw'] + o:s['raw'] + min(o + take, s['rsz'])] if o < s['rsz'] else b''
                out += chunk + bytes(take - len(chunk))
            va += take
            n -= take
        return bytes(out)

    def u32(self, va):
        return struct.unpack('<I', self.read(va, 4))[0]

    def f32(self, va):
        return struct.unpack('<f', self.read(va, 4))[0]

    def cstring(self, va, limit=120):
        """The printable C string at va, or None."""
        try:
            b = self.read(va, limit)
        except ValueError:
            return None
        e = b.find(b'\0')
        if e < 3 or any((c < 0x20 or c > 0x7e) and c not in (9, 10) for c in b[:e]):
            return None
        return b[:e].decode('latin1')

    def is_code(self, va):
        s = self.section_of(va)
        return bool(s and s['flags'] & SECTION_EXECUTABLE)

    def code_sections(self):
        return [s for s in self.sections if s['flags'] & SECTION_EXECUTABLE]

    def branch_sites(self):
        """target -> [(site, 'call' | 'jmp' | 'jcc')] for every rel32 call, jmp and conditional jump in the code.

        A byte scan: a match inside another instruction or in data is possible, so check a site with a
        disassembler before relying on it (mc3_xbe_xref does)."""
        if getattr(self, '_branches', None) is None:
            index = {}
            for s in self.code_sections():
                code = self.read(s['va'], min(s['vsz'], s['rsz']))
                for op, kind, length in ((b'\xe8', 'call', 5), (b'\xe9', 'jmp', 5)):
                    i = code.find(op)
                    while 0 <= i <= len(code) - length:
                        site = s['va'] + i
                        t = (site + length + struct.unpack_from('<i', code, i + 1)[0]) & 0xffffffff
                        if self.is_code(t):
                            index.setdefault(t, []).append((site, kind))
                        i = code.find(op, i + 1)
                i = code.find(b'\x0f')
                while 0 <= i <= len(code) - 6:
                    if 0x80 <= code[i + 1] <= 0x8f:
                        site = s['va'] + i
                        t = (site + 6 + struct.unpack_from('<i', code, i + 2)[0]) & 0xffffffff
                        if self.is_code(t):
                            index.setdefault(t, []).append((site, 'jcc'))
                    i = code.find(b'\x0f', i + 1)
            self._branches = index
        return self._branches

    def data_refs(self, value):
        """Every address (any alignment, any section) holding the 32-bit word `value`."""
        want = struct.pack('<I', value)
        out = []
        for s in self.sections:
            data = self.read(s['va'], min(s['vsz'], s['rsz']))
            i = data.find(want)
            while i >= 0:
                out.append(s['va'] + i)
                i = data.find(want, i + 1)
        return out

    # ----- names
    @property
    def names(self):
        if self._names is None:
            self._names = load_names()
        return self._names

    def name(self, va, default=None):
        if va in self.imports:
            return self.imports[va]
        return self.names.get(va, default)

    def nearest_name(self, va):
        """(start, name) of the last named code address at or below va."""
        if getattr(self, '_code_names', None) is None:
            self._code_names = sorted(a for a in self.names if self.is_code(a))
        i = bisect.bisect_right(self._code_names, va) - 1
        if i < 0:
            return None
        a = self._code_names[i]
        return a, self.names[a]


def open_xbe(path=None):
    path = path or os.environ.get('MC3_XBOX_XBE')
    if not path:
        raise SystemExit('set MC3_XBOX_XBE to the game\'s default.xbe (or pass its path)')
    return Xbe(path)


def default_name_files():
    env = os.environ.get('MC3_XBOX_NAMES')
    if env:
        return [p for p in env.split(os.pathsep) if p]
    root = os.environ.get('MC_RESEARCH_ROOT')
    here = pathlib.Path(__file__).resolve().parent
    candidates = [here.parent / 'mc3_xbox_names']
    if root:
        candidates.append(pathlib.Path(root) / 'midnight_club_3' / 'xbox' / 'reverse' / 'mc3_xbox_names')
    return [str(c) for c in candidates if c.exists()][:1]


def load_names(files=None):
    """address -> name from the name files (earlier files and earlier lines win)."""
    names = {}
    paths = []
    for p in files if files is not None else default_name_files():
        p = pathlib.Path(p)
        if p.is_dir():
            paths += sorted(q for q in p.iterdir() if q.suffix in ('.txt', '.tsv'))
        elif p.exists():
            paths.append(p)
    for p in paths:
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            if not line or line.startswith('#'):
                continue
            q = re.split(r'[\t ]+', line.strip(), maxsplit=2)
            if len(q) < 2:
                continue
            try:
                names.setdefault(int(q[0], 16), q[1])
            except ValueError:
                pass
    return names


def parse_address(text):
    """A hex address with or without 0x."""
    return int(text, 16)
