from .basetypes import *

class _SignedVarInt64Adapter(con.Adapter):
    def _decode(self, obj, context, path):
        res = obj - 1
        if res >= (1 << 63):
            res -= (1 << 64)
        return res

    def _encode(self, obj, context, path):
        obj = (obj + 1) & ((1 << 64) - 1)
        return obj

SignedVarInt64 = _SignedVarInt64Adapter(IdaVarInt64)
TypeInfoStringLength = con.ExprAdapter(IdaVarInt32, con.obj_ - 1, con.obj_ + 1)
TypeInfoString = con.PascalString(TypeInfoStringLength, "utf8")


# IDs for common types
CommonTypes = con.Enum(con.Byte,
    STI_PCHAR = 0x0,           #< char *
    STI_PUCHAR = 0x1,          #< uint8 *
    STI_PCCHAR = 0x2,          #< const char *
    STI_PCUCHAR = 0x3,         #< const uint8 *
    STI_PBYTE = 0x4,           #< _BYTE *
    STI_PINT = 0x5,            #< int *
    STI_PUINT = 0x6,           #< unsigned int *
    STI_PVOID = 0x7,           #< void *
    STI_PPVOID = 0x8,          #< void **
    STI_PCVOID = 0x9,          #< const void *
    STI_ACHAR = 0xA,           #< char[]
    STI_AUCHAR = 0xB,          #< uint8[]
    STI_ACCHAR = 0xC,          #< const char[]
    STI_ACUCHAR = 0xD,         #< const uint8[]
    STI_FPURGING = 0xE,        #< void __userpurge(int)
    STI_FDELOP = 0xF,          #< void __cdecl(void *)
    STI_MSGSEND = 0x10,        #< void *(void *, const char *, ...)
    STI_AEABI_LCMP = 0x11,     #< int __fastcall(int64 x, int64 y)
    STI_AEABI_ULCMP = 0x12,    #< int __fastcall(uint64 x, uint64 y)
    STI_DONT_USE = 0x13,       #< unused stock type id; should not be used
    STI_SIZE_T = 0x14,         #< size_t
    STI_SSIZE_T = 0x15,        #< ssize_t
    STI_AEABI_MEMCPY = 0x16,   #< void __fastcall(void *, const void *, size_t)
    STI_AEABI_MEMSET = 0x17,   #< void __fastcall(void *, size_t, int)
    STI_AEABI_MEMCLR = 0x18,   #< void __fastcall(void *, size_t)
    STI_RTC_CHECK_2 = 0x19,    #< int16 __fastcall(int16 x)
    STI_RTC_CHECK_4 = 0x1A,    #< int32 __fastcall(int32 x)
    STI_RTC_CHECK_8 = 0x1B,    #< int64 __fastcall(int64 x)
    STI_LAST = 0x1C,
)

# ref tf_mask
TYPE_SIZE  = con.BitsInteger(4)   #TYPE_BASE_MASK  = 0x0F
FLAGS_SIZE = con.BitsInteger(2)   #TYPE_FLAGS_MASK = 0x30
MOD_SIZE   = con.BitsInteger(2)   #TYPE_MODIF_MASK = 0xC0


# ref tf
BaseTypes = con.Enum(TYPE_SIZE,
    BT_UNK         = 0x00,     #< unknown
    BT_VOID        = 0x01,     #< void
    BT_INT8        = 0x02,     #< __int8
    BT_INT16       = 0x03,     #< __int16
    BT_INT32       = 0x04,     #< __int32
    BT_INT64       = 0x05,     #< __int64
    BT_INT128      = 0x06,     #< __int128 (for alpha & future use)
    BT_INT         = 0x07,     #< natural int. (size provided by idp module)
    BT_BOOL        = 0x08,     #< bool
    BT_FLOAT       = 0x09,     #< float
    BT_PTR         = 0x0A,     #< pointer.
    BT_ARRAY       = 0x0B,     #< array
    BT_FUNC        = 0x0C,     #< function.
    BT_COMPLEX     = 0x0D,     #< struct/union/enum/typedef.
    BT_BITFIELD    = 0x0E,     #< bitfield (only in struct)
    BT_RESERVED    = 0x0F,     #< RESERVED
)
#BT_INT might be a bit of a pain to support across archs

# start basic type flags

# ref tf_unk
VoidFlags = con.Enum(FLAGS_SIZE,
    BTMT_SIZE0   = 0x0,        #< ::BT_VOID - normal void; ::BT_UNK - don't use
    BTMT_SIZE12  = 0x1,        #< size = 1  byte  if ::BT_VOID; 2 if ::BT_UNK
    BTMT_SIZE48  = 0x2,        #< size = 4  bytes if ::BT_VOID; 8 if ::BT_UNK
    BTMT_SIZE128 = 0x3,        #< size = 16 bytes if ::BT_VOID; unknown if ::BT_UNK
                               #< (IN struct alignment - see below)
)

# ref tf_int
IntFlags = con.Enum(FLAGS_SIZE,
    BTMT_UNKSIGN = 0x0,        #< unknown signedness
    BTMT_SIGNED  = 0x1,        #< signed
    BTMT_USIGNED = 0x2,        #< unsigned
    BTMT_CHAR    = 0x3,        #< specify char or segment register
                               #< - ::BT_INT8         - char
                               #< - ::BT_INT          - segment register
                               #< - other BT_INT...   - don't use
)

# ref tf_bool
BoolFlags = con.Enum(FLAGS_SIZE,
    BTMT_DEFBOOL = 0x0,        #< size is model specific or unknown(?)
    BTMT_BOOL1   = 0x1,        #< size 1byte
    BTMT_BOOL2OR8= 0x2,        #< size 2bytes - !inf_is_64bit(); size 8bytes - inf_is_64bit()
    BTMT_BOOL4   = 0x3,        #< size 4bytes
)
#pain another arch dependent flag

# ref tf_float
FloatFlags = con.Enum(FLAGS_SIZE,
    BTMT_FLOAT   = 0x0,        #< float (4 bytes)
    BTMT_DOUBLE  = 0x1,        #< double (8 bytes)
    BTMT_LNGDBL  = 0x2,        #< long double (compiler specific)
    BTMT_SPECFLT = 0x3,        #< float (variable size).
                               #< if \ph{use_tbyte()} then use \ph{tbyte_size},
                               #< otherwise 2 bytes
)

# end basic type flags (ref tf_last_basic)

# ref tf_ptr
PtrFlags = con.Enum(FLAGS_SIZE,
    BTMT_DEFPTR  = 0x0,        #< default for model
    BTMT_NEAR    = 0x1,        #< near
    BTMT_FAR     = 0x2,        #< far
    BTMT_CLOSURE = 0x3,        #< closure.
                               #< - if ptr to ::BT_FUNC - __closure.
                               #<   in this case next byte MUST be
                               #<   #RESERVED_BYTE, and after it ::BT_FUNC
                               #< - else the next byte contains sizeof(ptr)
                               #<   allowed values are 1 - \varmem{ph,processor_t,max_ptr_size}
                               #< - if value is bigger than \varmem{ph,processor_t,max_ptr_size},
                               #<   based_ptr_name_and_size() is called to
                               #<   find out the typeinfo
)

# ref tf_array
ArrayFlags = con.Enum(FLAGS_SIZE,
    BTMT_NONBASED  = 0x1,      #< \code
                               # if set
                               #    array base==0
                               #    format: dt num_elem; [tah-typeattrs]; type_t...
                               #    if num_elem==0 then the array size is unknown
                               # else
                               #    format: da num_elem, base; [tah-typeattrs]; type_t... \endcode
                               # used only for serialization
    BTMT_ARRESERV  = 0x2,      #< reserved bit
)

# ref tf_func
FuncFlags = con.Enum(FLAGS_SIZE,
    BTMT_DEFCALL  = 0x0,       #< call method - default for model or unknown
    BTMT_NEARCALL = 0x1,       #< function returns by retn
    BTMT_FARCALL  = 0x2,       #< function returns by retf
    BTMT_INTCALL  = 0x3,       #< function returns by iret
                               #< in this case cc MUST be 'unknown'
)

# ref tf_complex
ComplexFlags = con.Enum(FLAGS_SIZE,
    BTMT_STRUCT  = 0x0,        #<     struct:
                               #<       MCNT records: type_t; [sdacl-typeattrs];
    BTMT_UNION   = 0x1,        #<     union:
                               #<       MCNT records: type_t...
    BTMT_ENUM    = 0x2,        #<     enum:
                               #<       next byte bte_t (see below)
                               #<       N records: de delta(s)
                               #<                  OR
                               #<                  blocks (see below)
    BTMT_TYPEDEF = 0x3,        #< named reference
                               #<   always p_string name
)

BitFieldFlags = con.Enum(FLAGS_SIZE,
    BTMT_BFLDI8    = 0x0,      #< __int8
    BTMT_BFLDI16   = 0x1,      #< __int16
    BTMT_BFLDI32   = 0x2,      #< __int32
    BTMT_BFLDI64   = 0x3,      #< __int64
)

# end flags

FlagsMapping = con.Switch(lambda this: this.basetype, {
    BaseTypes.BT_VOID    : VoidFlags,
    BaseTypes.BT_INT8    : IntFlags,
    BaseTypes.BT_INT16   : IntFlags,
    BaseTypes.BT_INT32   : IntFlags,
    BaseTypes.BT_INT64   : IntFlags,
    BaseTypes.BT_INT128  : IntFlags,
    BaseTypes.BT_INT     : IntFlags,
    BaseTypes.BT_BOOL    : BoolFlags,
    BaseTypes.BT_FLOAT   : FloatFlags,
    BaseTypes.BT_PTR     : PtrFlags,
    BaseTypes.BT_ARRAY   : ArrayFlags,
    BaseTypes.BT_FUNC    : FuncFlags,
    BaseTypes.BT_COMPLEX : ComplexFlags,
    BaseTypes.BT_BITFIELD: BitFieldFlags,
}, default=FLAGS_SIZE)   #leave it as bits


# ref tf_modifiers
Modifiers = con.Enum(MOD_SIZE,
    BTM_NONE = 0x0,          #(non-IDA) signifies no modifiers
    BTM_CONST = 0x1,         #< const
    BTM_VOLATILE = 0x2,      #< volatile
)

#typedef uchar type_t - 4/2/2 bits, see ref tf
type_t = con.Restreamed(con.Struct(
    "basetype" / BaseTypes,
    "flags" / FlagsMapping,
    "modifiers" / Modifiers,
), lambda data: (s:=con.bytes2bits(data))[4:]+s[2:4]+s[:2], 1
, lambda data: con.bits2bytes(data[:2]+data[2:4]+data[:4]), 8, 1)  #we know type_t is 1 byte, so no need for a lambda
#reorders the bitfields so FlagsMapping can parse correctly


@singleton
class TypeInfo(Construct):
    r"""
    construct adapter that handles (de)serialization of tinfo_t
    """

    def _parse(self, stream, context, path):
        typedef = type_t.parse_stream(stream)

        unparsed = con.GreedyBytes.parse_stream(stream)

        return con.Container(type=typedef, data=unparsed)

    def _build(self, obj, stream, context, path):
        return obj