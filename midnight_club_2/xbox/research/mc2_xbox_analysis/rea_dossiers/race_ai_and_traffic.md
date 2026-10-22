# REA Dossier: Races, Ambient, Helicopters, Traffic & Trains (`race_ai_and_traffic`)

- **REA Evidence ID:** `ev_6ab9a545ae9a0aeeaa33ac7da646fbaed5d61b34f66c3a351dd4573f8682e296`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 146
- **Hex-Rays Decompiled Functions:** 43

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

### `Main_void`
- **MC2 Xbox VA:** `0x011130..0x113a4` (509 B) | **MC3 Xbox VA:** `0x012440` (553 B, delta: `+44 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_ca691e745a6b9264ccd477607539e1985f2fe0f3798eb4e8149178a4f02dfe38`

```cpp
int __userpurge Main_void@<eax>(int a1@<ebx>, int a2@<edi>, int a3@<esi>, int a4, const char *a5)
{
  char v5; // bl
  int v6; // esi
  int v7; // eax
  int v8; // ecx
  int v9; // edx
  int v11; // [esp-4h] [ebp-Ch]
  const char *v12; // [esp+0h] [ebp-8h] BYREF
  int v13; // [esp+4h] [ebp-4h]

  sub_1E9C80(a2, a3, a1);
  off_35484C = &byte_100000;
  dword_354850 = 0x8000;
  byte_543AE8 = 1;
  byte_356D40 = 0;
  mcConfig__ParseUnlockCommandLineParams_void();
  vt_6240a8__slot_4();
  if ( sub_14DA90() != -1 )
    dword_3AC6DC = sub_14DA90();
  sub_1CE340();
  byte_3B66A1 = 1;
  v12 = "T:\\mc2\\assets_x";
  sub_208060("path", 0, &v12);
  sub_14E560(v12, 46, 0, 0, 0);
  dword_375E90 = (int)off_356DD4[0];
  qmemcpy(&unk_375E94, off_356DD4[0], 0x28u);
  dword_375E9C = (int)sub_110A0;
  off_356DD4[0] = (int (__cdecl **)(int, char))&unk_375E94;
  mcConfig__ParseStartupAndRaceCommandLineParams_void();
  v5 = sub_207FC0("runforever");
  vt_6240a8__slot_4();
  do
  {
    sub_14E580("assets_x.dat");
    vt_6240a8__slot_4();
    v6 = sub_17FB0();
    sub_17430(v6);
    sub_181E0();
    sub_1A3F0();
    if ( (unsigned __int8)sub_207FC0("nofe") )
    {
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 6);
    }
    else if ( (unsigned __int8)sub_207FC0("carview") )
    {
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 20);
    }
    else if ( (unsigned __int8)sub_207FC0("raceed") )
    {
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 19);
    }
    else if ( (unsigned __int8)sub_207FC0("movie") )
    {
      a5 = "angel.imf";
      sub_208060("movie", 0, &a5);
      sub_14E9F0(a5);
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 15);
    }
    else if ( (unsigned __int8)sub_207FC0("skipintro") || byte_3AC6E4 )
    {
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 17);
    }
    else
    {
      sub_14E9F0("rockstar.pss");
      (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 15);
    }
    sub_17CD0(v6);
    sub_14E630();
    sub_17FE0();
    sub_173B0();
    sub_14E5F0();
  }
  while ( v5 );
  sub_20D699(0);
  sub_11F28();
  sub_11BF4();
  v7 = *((_DWORD *)NtCurrentTeb()->ClientId.UniqueProcess + 148);
  if ( v7 )
    v8 = *(_DWORD *)(v7 + 36);
  else
    v8 = 0;
  if ( v8 )
  {
    v13 = v11;
    v9 = *((_DWORD *)NtCurrentTeb()->NtTib.StackBase + TlsIndex) - *((_DWORD *)NtCurrentTeb()->ActiveRpcHandle + 10);
    *(_BYTE *)v8 = 1;
    *(_DWORD *)(v8 + 4) = v9 + 4;
  }
  sub_11DC9();
  sub_11D71();
  v13 = 0;
  sub_11000(0, 0);
  sub_118FE(1, 1, 0);
  return 0;
}

```

### `mcLayerRace__Load_void`
- **MC2 Xbox VA:** `0x01F708..0x1f88b` (392 B) | **MC3 Xbox VA:** `0x029200` (11 B, delta: `-381 B`) | **MC3 PS2 VA:** `0x1A9C88`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_9d973ac9d3597a142bea76d7dcfdb14c43abd86113f756065a9996d899bcc2b1`

```cpp
// positive sp value has been detected, the output may be wrong!
int __usercall mcLayerRace__Load_void@<eax>(int a1@<ebx>, int a2@<edi>)
{
  int i; // esi
  int v3; // eax
  int v4; // esi
  int v5; // eax
  int v6; // eax
  int result; // eax

  dword_540394 = (int)"popup";
  txtStringTable__Load_char_const__ptr__txtLanguage__eLanguage_unsigned_int_bool_bool("mcstrings_x", dword_3AC6DC, 2, 0);
  *(_DWORD *)(a2 + 24) = sub_1789E0(16);
  for ( i = 0; i < 4; ++i )
    *(_DWORD *)(i * 4 + *(_DWORD *)(a2 + 24)) = txtGetFontTex_char_const__ptr__bool(off_34DC5C[i], 0);
  vt_6240a8__slot_4();
  sub_C2490();
  sub_11A4F0();
  sub_930C0();
  ((void (__thiscall *)(int))sub_928E0)(dword_3813D0);
  sub_AA260();
  sub_E6910("weapons");
  sub_DBBD0();
  opponentIconTuneData__InitStaticData_void();
  sub_123200();
  sub_1222C0();
  vt_6240a8__slot_4();
  mcSpark__init_void();
  mcLightning__initStaticData_void();
  sub_AC370();
  v3 = sub_C20F0();
  LOBYTE(v3) = a1 != 0;
  sub_C22E0(v3);
  ((void (__thiscall *)(int))sub_112E20)(dword_386090);
  sub_B1340(7);
  sub_953A0();
  if ( a1 )
    ((void (__thiscall *)(int))sub_2090E0)(a1);
  mcPlayerManager__CreateInstance_void();
  ((void (__thiscall *)(int))sub_7DBF0)(dword_37FFE4);
  sub_7FB50();
  ((void (__thiscall *)(int))sub_7F9D0)(dword_37FFF0);
  ((void (__thiscall *)(int))sub_141680)(dword_3B6774);
  ((void (__thiscall *)(int))sub_928D0)(dword_3813D0);
  sub_1208C0();
  sub_1ECA30();
  sub_1EE9F0();
  sub_1AE90();
  sub_176940();
  v4 = dword_375EF8;
  v5 = _builtin_new(48);
  if ( v5 )
    v6 = ((int (__thiscall *)(int))sub_17B80)(v5);
  else
    v6 = 0;
  *(_DWORD *)(v4 + 4) = v6;
  vt_6240a8__slot_4();
  result = ((int (__thiscall *)(int))sub_1308E0)(dword_3ABF24 + 544);
  *(_BYTE *)(a2 + 4) = 1;
  return result;
}

```

### `mcPropType__LoadTypeData_char_const__ptr__char_const__ptr`
- **MC2 Xbox VA:** `0x091370..0x91f6f` (3072 B) | **MC3 Xbox VA:** `0x19D980` (4975 B, delta: `+1903 B`) | **MC3 PS2 VA:** `0x395460`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_21b7b5cebe42f91994247355f03289762c51846026111f428049523d4bf4fab7`

```cpp
int __thiscall mcPropType__LoadTypeData_char_const__ptr__char_const__ptr(int this, int a2)
{
  int v3; // eax
  char v5; // al
  int v6; // eax
  int v7; // eax
  int v8; // eax
  int v9; // ebx
  char v10; // al
  char v11; // al
  unsigned int v12; // ebx
  const char *v13; // ebx
  int v14; // eax
  int v15; // edi
  int v16; // ebx
  double v17; // st7
  double v18; // st7
  double v19; // st6
  double v20; // st5
  long double v21; // st7
  double v22; // st7
  double v23; // st6
  double v24; // st5
  double v25; // st5
  double v26; // st7
  double v27; // st6
  int v28; // eax
  double v29; // st7
  _DWORD *v30; // eax
  int v31; // eax
  int v32; // eax
  int v33; // eax
  int v34; // ebx
  int v35; // edx
  float *v36; // eax
  float v37; // edx
  float v38; // ecx
  int v39; // eax
  int v40; // eax
  char *v41; // edi
  int ModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int; // eax
  _DWORD *v44; // edi
  int v45; // eax
  float *v46; // ebx
  float v47; // ecx
  float v48; // eax
  int v49; // ecx
  int v50; // eax
  float *v51; // ebx
  double v52; // st7
  double v53; // st6
  double v54; // st7
  double v55; // st6
  double v56; // st6
  long double v57; // st4
  long double v58; // st7
  int v60; // [esp+0h] [ebp-2E4h]
  int v61; // [esp+0h] [ebp-2E4h]
  float v62; // [esp+14h] [ebp-2D0h] BYREF
  float v63; // [esp+18h] [ebp-2CCh]
  float v64; // [esp+1Ch] [ebp-2C8h]
  float v65; // [esp+20h] [ebp-2C4h] BYREF
  float v66; // [esp+24h] [ebp-2C0h]
  float v67; // [esp+28h] [ebp-2BCh]
  float v68; // [esp+2Ch] [ebp-2B8h]
  float v69; // [esp+30h] [ebp-2B4h]
  float v70; // [esp+34h] [ebp-2B0h]
  float v71; // [esp+38h] [ebp-2ACh]
  int v72; // [esp+3Ch] [ebp-2A8h]
  _DWORD *v73; // [esp+40h] [ebp-2A4h]
  int v74; // [esp+44h] [ebp-2A0h]
  float v75; // [esp+48h] [ebp-29Ch]
  float v76; // [esp+4Ch] [ebp-298h]
  float v77; // [esp+50h] [ebp-294h]
  int v78; // [esp+54h] [ebp-290h]
  int v79; // [esp+58h] [ebp-28Ch]
  float *v80; // [esp+5Ch] [ebp-288h]
  float v81; // [esp+60h] [ebp-284h] BYREF
  float v82; // [esp+64h] [ebp-280h]
  float v83; // [esp+68h] [ebp-27Ch]
  float v84; // [esp+6Ch] [ebp-278h]
  float v85; // [esp+70h] [ebp-274h]
  float v86; // [esp+74h] [ebp-270h]
  float v87[3]; // [esp+78h] [ebp-26Ch] BYREF
  _DWORD v88[23]; // [esp+84h] [ebp-260h] BYREF
  float v89; // [esp+E0h] [ebp-204h] BYREF
  char v90[64]; // [esp+E4h] [ebp-200h] BYREF
  _BYTE v91[64]; // [esp+124h] [ebp-1C0h] BYREF
  _BYTE v92[64]; // [esp+164h] [ebp-180h] BYREF
  char v93[64]; // [esp+1A4h] [ebp-140h] BYREF
  _BYTE v94[256]; // [esp+1E4h] [ebp-100h] BYREF

  if ( !dword_3813CC )
  {
    if ( _builtin_new(52) )
      v3 = sub_15CE60(1024);
    else
      v3 = 0;
    dword_3813CC = v3;
    sub_119C00(v3);
  }
  datBaseTokenizer__MatchToken_char_const__ptr("prop_template");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v94, 256);
  *(_DWORD *)(this + 4) = StringDuplicate_char_const__ptr(v94);
  datBaseTokenizer__MatchToken_char_const__ptr("{");
  datBaseTokenizer__MatchToken_char_const__ptr("animation:");
  v5 = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
  *(_BYTE *)(this + 10) = v5;
  if ( v5 )
  {
    v6 = _builtin_new(12);
    if ( v6 )
      v7 = sub_1DE6B0(v6);
    else
      v7 = 0;
    v60 = *(_DWORD *)(this + 4);
    *(_DWORD *)(this + 12) = v7;
    if ( (unsigned __int8)sub_1DECE0(v60) )
    {
      v8 = sub_1DD1C0(*(float *)(this + 4), 1);
      *(_DWORD *)(this + 16) = v8;
      sub_90D00(v8);
    }
    else
    {
      v9 = *(_DWORD *)(this + 12);
      if ( v9 )
      {
        sub_1DE6D0(*(_DWORD *)(this + 12));
        _builtin_delete(v9);
      }
      *(_DWORD *)(this + 12) = 0;
      *(_BYTE *)(this + 10) = 0;
    }
  }
  datBaseTokenizer__MatchToken_char_const__ptr("numparts:");
  v10 = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
  *(_BYTE *)(this + 11) = v10;
  v74 = 0;
  v72 = 0;
  if ( v10 )
  {
    *(_DWORD *)(this + 24) = _builtin_new(4 * v10);
    v11 = *(_BYTE *)(this + 11);
    v79 = 0;
    if ( v11 > 0 )
    {
      v80 = (float *)(this + 92);
      v73 = (_DWORD *)(this + 60);
      do
      {
        datBaseTokenizer__MatchToken_char_const__ptr("part");
        (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
        datBaseTokenizer__MatchToken_char_const__ptr("{");
        datBaseTokenizer__MatchToken_char_const__ptr("name:");
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v90, 64);
        v12 = strlen(*(const char **)(this + 4));
        datBaseTokenizer__MatchToken_char_const__ptr("offset:");
        (*(void (__thiscall **)(int, float *))(*(_DWORD *)a2 + 36))(a2, &v81);
        datBaseTokenizer__MatchToken_char_const__ptr("}");
        v13 = &v90[v12 + 1];
        if ( !strncmp(v13, "particle", 8) )
        {
          if ( !strncmp(v13, "particle_explosion", 18) )
          {
            *(_DWORD *)(this + 316) |= 2u;
          }
          else if ( !strncmp(v13, "particle_spark", 14) )
          {
            *(_DWORD *)(this + 316) |= 1u;
            v39 = _builtin_new(6528);
            if ( v39 )
              v40 = sub_8C9A0(v39);
            else
              v40 = 0;
            v61 = *(_DWORD *)(this + 4);
            *(_DWORD *)(this + 312) = v40;
            parFileIO__SetName_char_const__ptr(v61);
            sub_1E2E50(*(_DWORD *)(this + 312));
          }
          else
          {
            v41 = (char *)&v89 + 3;
            while ( *++v41 )
              ;
            strcpy(v41, "_0");
            ModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int = gfxGetModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int(
                                                                               dword_3ABF24 + 264,
                                                                               v90,
                                                                               0,
                                                                               274);
            *(v73 - 8) = ModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int;
            if ( ModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int )
            {
              v44 = v73;
              *v73 = ***(_DWORD ***)(ModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int + 4);
              strlen(v92, 64, "%s", v13);
              v44[32] = sub_8CA30(v92);
              strncmp(v13, "particle_firehydrant", 20);
              swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(*v44, 8, 8);
              v45 = dword_3813CC;
              *(_DWORD *)(dword_3813CC + 44) = *v44;
              v46 = v80;
              *(_DWORD *)(v45 + 48) = 8;
              v47 = v82;
              *v46 = v81;
              v48 = v83;
              v46[1] = v47;
              v46[2] = v48;
              strlen(v93, 64, "too many particle types attached to %s\n", off_34F2E4[dword_3ACD38]);
              ++v72;
              v73 = v44 + 1;
              v80 = v46 + 3;
            }
          }
        }
        else if ( !strncmp(v13, "glass", 5) )
        {
          strlen(v91, 64, "%s_0", v90);
          v14 = gfxGetModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int(dword_3ABF24 + 264, v91, 0, 274);
          v15 = v14;
          if ( v14 )
          {
            v16 = 0;
            *(_DWORD *)(this + 316) |= 4u;
            v65 = 0.0;
            v66 = 0.0;
            v67 = 0.0;
            v78 = 0;
            if ( sub_1EE930(v14) > 0 )
            {
              do
              {
                sub_1EE9B0(&v62, v16++);
                v65 = v65 + v62;
                v66 = v66 + v63;
                v67 = v64 + v67;
              }
              while ( v16 < sub_1EE930(v15) );
              v78 = v16;
            }
            v17 = 1.0 / (double)v78;
            v65 = v65 * v17;
            v66 = v66 * v17;
            v67 = v67 * v17;
            sub_1EE9B0(&v62, 0);
            v75 = v65 - v62;
            v76 = v66 - v63;
            v77 = v67 - v64;
            sub_1EE9B0(&v62, 1);
            v18 = v65 - v62;
            v19 = v66 - v63;
            v20 = v67 - v64;
            v68 = v76 * v20 - v19 * v77;
            v69 = v77 * v18 - v20 * v75;
            v70 = v19 * v75 - v76 * v18;
            v21 = v70 * v70 + v69 * v69 + v68 * v68;
            if ( v21 == 0.0 )
              v71 = 0.0;
            else
              v71 = 1.0 / sqrt(v21);
            v22 = v71 * v68;
            v23 = v69 * v71;
            v24 = v70 * v71;
            v70 = v24;
            v25 = v24 * -1.0;
            if ( (v23 + v22) * 0.0 + v25 < 0.0 )
            {
              v22 = v22 * -1.0;
              v23 = v23 * -1.0;
              v70 = v25;
            }
            v87[0] = v22 + v65;
            v87[1] = v23 + v66;
            v87[2] = v70 + v67;
            sub_1FD8F0(&v65, v87);
            sub_1FD2B0(v88);
            v26 = *(float *)&v88[15] * v63 + *(float *)&v88[12] * v62 + *(float *)&v88[18] * v64 + *(float *)&v88[21];
            v27 = *(float *)&v88[16] * v63 + *(float *)&v88[13] * v62 + *(float *)&v88[19] * v64 + *(float *)&v88[22];
            v64 = *(float *)&v88[17] * v63 + *(float *)&v88[14] * v62 + *(float *)&v88[20] * v64 + v89;
            v62 = v26;
            v63 = v27;
            v28 = _builtin_new(76);
            v29 = v62;
            *(_DWORD *)(this + 320) = v28;
            *(float *)(v28 + 52) = fabs(v29 + v29);
            *(float *)(*(_DWORD *)(this + 320) + 56) = fabs(v63 + v63);
            *(_DWORD *)(*(_DWORD *)(this + 320) + 60) = 10;
            *(_DWORD *)(*(_DWORD *)(this + 320) + 64) = 10;
            v30 = (_DWORD *)(*(_DWORD *)(this + 320) + 4);
            *v30 = v88[0];
            v30[1] = v88[1];
            v30[2] = v88[2];
            v30[3] = v88[3];
            v30[4] = v88[4];
            v30[5] = v88[5];
            v30[6] = v88[6];
            v30[7] = v88[7];
            v30[8] = v88[8];
            v30[9] = v88[9];
            v30[10] = v88[10];
            v30[11] = v88[11];
            **(_DWORD **)(this + 320) = ***(_DWORD ***)(v15 + 4);
            v31 = **(_DWORD **)(this + 320);
            if ( v31 )
              ++*(_DWORD *)(v31 + 24);
            *(_DWORD *)(*(_DWORD *)(this + 320) + 68) = 1065353216;
            *(_DWORD *)(*(_DWORD *)(this + 320) + 72) = 1065353216;
            sub_1EFEE0(v15);
          }
        }
        else
        {
          v32 = _builtin_new(16);
          if ( v32 )
            v33 = sub_8C8E0(v32);
          else
            v33 = 0;
          v34 = v74;
          *(_DWORD *)(*(_DWORD *)(this + 24) + 4 * v74) = v33;
          sub_8C8F0(v90);
          v84 = v81;
          v35 = *(_DWORD *)(this + 24);
          v85 = v82;
          v36 = *(float **)(v35 + 4 * v34);
          v37 = v82;
          v86 = v83;
          *++v36 = v81;
          v38 = v86;
          v36[1] = v37;
          v36[2] = v38;
          v74 = v34 + 1;
        }
        v49 = *(char *)(this + 11);
        ++v79;
      }
      while ( v79 < v49 );
    }
    v50 = v72;
    *(_BYTE *)(this + 11) = v74;
    *(_DWORD *)(this + 220) = v50;
  }
  else
  {
    *(_DWORD *)(this + 24) = 0;
  }
  if ( !(unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("constraint", 1) )
  {
    *(_DWORD *)(this + 228) = 3;
    *(_DWORD *)(this + 232) = 0;
    *(_DWORD *)(this + 240) = 0;
    *(_DWORD *)(this + 236) = 1065353216;
    *(_DWORD *)(this + 244) = 3;
    *(_DWORD *)(this + 248) = 0;
    *(_DWORD *)(this + 252) = 1065353216;
    *(_DWORD *)(this + 256) = 0;
    *(_DWORD *)(this + 264) = -1082130432;
    *(_DWORD *)(this + 268) = 0;
    *(_DWORD *)(this + 272) = 0;
    *(_DWORD *)(this + 276) = 0;
    *(_DWORD *)(this + 280) = 0;
    *(_DWORD *)(this + 284) = 1065353216;
    *(_DWORD *)(this + 260) = 1069614331;
    *(_DWORD *)(this + 288) = 1082130432;
    goto LABEL_72;
  }
  datBaseTokenizer__MatchToken_char_const__ptr("{");
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("translationDOF:", 1) )
  {
    *(_DWORD *)(this + 228) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
    datBaseTokenizer__MatchToken_char_const__ptr("translationDir:");
    (*(void (__thiscall **)(int, int))(*(_DWORD *)a2 + 36))(a2, this + 232);
    *(_BYTE *)(this + 224) = 1;
  }
  else
  {
    *(_DWORD *)(this + 228) = 3;
    *(_DWORD *)(this + 232) = 0;
    *(_DWORD *)(this + 236) = 1065353216;
    *(_DWORD *)(this + 240) = 0;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("rotationDOF:", 1) )
  {
    *(_DWORD *)(this + 244) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
    datBaseTokenizer__MatchToken_char_const__ptr("rotationDir:");
    v51 = (float *)(this + 248);
    (*(void (__thiscall **)(int, int))(*(_DWORD *)a2 + 36))(a2, this + 248);
    if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("rotationLim:", 1) )
      *(float *)(this + 260) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
    if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("rotationRestore:", 1) )
      *(float *)(this + 288) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
    *(_BYTE *)(this + 224) = 1;
  }
  else
  {
    *(_DWORD *)(this + 244) = 3;
    v51 = (float *)(this + 248);
    *(_DWORD *)(this + 248) = 0;
    *(_DWORD *)(this + 252) = 1065353216;
    *(_DWORD *)(this + 256) = 0;
    *(_DWORD *)(this + 260) = 1069614331;
    *(_DWORD *)(this + 288) = 1082130432;
  }
  if ( fabs(*v51) > 0.5 )
  {
    v52 = -*v51;
    v53 = *(float *)(this + 256);
    *(_DWORD *)(this + 268) = 0;
    *(float *)(this + 264) = v53;
LABEL_66:
    *(float *)(this + 272) = v52;
    goto LABEL_67;
  }
  if ( fabs(*(float *)(this + 252)) <= 0.5 )
  {
    v52 = *(float *)(this + 252);
    v56 = *v51;
    *(_DWORD *)(this + 264) = 0;
    *(float *)(this + 268) = -v56;
    goto LABEL_66;
  }
  v54 = *v51;
  v55 = *(float *)(this + 252);
  *(_DWORD *)(this + 272) = 0;
  *(float *)(this + 264) = -v55;
  *(float *)(this + 268) = v54;
LABEL_67:
  v57 = *(float *)(this + 264) * *(float *)(this + 264)
      + *(float *)(this + 268) * *(float *)(this + 268)
      + *(float *)(this + 272) * *(float *)(this + 272);
  if ( v57 == 0.0 )
    v58 = 0.0;
  else
    v58 = 1.0 / sqrt(v57);
  *(float *)(this + 264) = v58 * *(float *)(this + 264);
  *(float *)(this + 268) = v58 * *(float *)(this + 268);
  *(float *)(this + 272) = v58 * *(float *)(this + 272);
  *(float *)(this + 276) = v51[1] * *(float *)(this + 272) - v51[2] * *(float *)(this + 268);
  *(float *)(this + 280) = *(float *)(this + 264) * v51[2] - *v51 * *(float *)(this + 272);
  *(float *)(this + 284) = *v51 * *(float *)(this + 268) - *(float *)(this + 264) * v51[1];
  datBaseTokenizer__MatchToken_char_const__ptr("}");
LABEL_72:
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("FixedObject:", 1) )
    *(_BYTE *)(this + 324) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 8))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Obstacle:", 1) )
    *(_BYTE *)(this + 325) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 8))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("GfxOnly:", 1) )
    *(_BYTE *)(this + 326) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 8))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Drivable:", 1) )
    *(_BYTE *)(this + 327) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 8))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Far:", 1) )
    *(_BYTE *)(this + 328) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 8))(a2);
  return datBaseTokenizer__MatchToken_char_const__ptr("}");
}

```

### `mcMenuRaceOver__PopulateMenu_int`
- **MC2 Xbox VA:** `0x098186..0x983ac` (550 B) | **MC3 Xbox VA:** `0x16BFA0` (2721 B, delta: `+2171 B`) | **MC3 PS2 VA:** `0x35AA10`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_2e750e8cd67f2535c6eeee53d835771e87caf2c448d461af81349b6906a5fbda`

```cpp
int __userpurge mcMenuRaceOver__PopulateMenu_int@<eax>(
        int a1@<ebx>,
        int a2@<esi>,
        int a3,
        int a4,
        int a5,
        int a6,
        int a7,
        int a8,
        int a9,
        int a10,
        int a11)
{
  char *v11; // esi
  _DWORD *v13; // eax
  _DWORD *v14; // eax
  int v15; // eax
  int v16; // edi

  v11 = (char *)dword_3ACEA4 + a2;
  *(_DWORD *)(a1 + 40) = sub_153CA0(v11);
  *(_DWORD *)(a1 + 68) = sub_153CB0(v11);
  if ( *(_DWORD *)(dword_3AD2F8 + 4) == 3 )
  {
    *(_BYTE *)(*(_DWORD *)(a1 + 76) + 376) = 12;
    (*(void (__thiscall **)(int))(*(_DWORD *)dword_3B6774 + 4))(dword_3B6774);
    if ( *(_BYTE *)(dword_375F1C + 52) )
    {
      sub_B25E0("EndReplay");
    }
    else
    {
      v13 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_945A0, a1);
      sub_B3470(
        "ContinueReplay",
        0,
        0,
        *v13,
        v13[1],
        v13[2],
        v13[3],
        0,
        dword_543E20,
        dword_543E24,
        dword_543E28,
        dword_543E2C);
      a11 = 1;
    }
    *(_BYTE *)(a1 + 123) = 0;
    v14 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_945F0, a1);
    sub_B3470(
      "RestartReplay",
      a11,
      0,
      *v14,
      v14[1],
      v14[2],
      v14[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
  }
  else
  {
    *(_BYTE *)(*(_DWORD *)(a1 + 76) + 376) = 10;
    sub_140CB0(dword_3B6774);
  }
  if ( dword_3AC6E0 != 2 )
    JUMPOUT(0x98479);
  if ( !*(_BYTE *)(a1 + 4) )
    JUMPOUT(0x9842E);
  v15 = sub_9E210(0);
  v16 = v15;
  if ( !v15 )
    goto LABEL_23;
  if ( !strcasecmp("mauro", v15) )
  {
    datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_94650, a1);
    JUMPOUT(0x986FD);
  }
  if ( !*(_BYTE *)(a1 + 252) || !strcasecmp("savo", v16) )
LABEL_23:
    JUMPOUT(0x983E3);
  datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_94650, a1);
  return mcMenuRaceOver__HandleCareerAndCruiseSelection_int(a3);
}

```

### `mcMenuRaceOver__HandleCareerAndCruiseSelection_int`
- **MC2 Xbox VA:** `0x0983AC..0x98c53` (2071 B) | **MC3 Xbox VA:** `0x16B51E` (802 B, delta: `-1269 B`) | **MC3 PS2 VA:** `0x34FFD0`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_28ae7fe34360ad723dbd2eeff7b239e1af72a0c07d0c612d44d43bca713266bc`

```cpp
// positive sp value has been detected, the output may be wrong!
int __userpurge mcMenuRaceOver__HandleCareerAndCruiseSelection_int@<eax>(
        _DWORD *a1@<eax>,
        int a2@<ecx>,
        int a3@<ebx>,
        int a4@<esi>,
        int a5,
        int a6,
        int a7,
        int a8,
        int a9,
        int a10,
        int a11,
        int a12)
{
  int v12; // esi
  _DWORD *v13; // eax
  int v14; // esi
  _DWORD *v15; // eax
  _DWORD *v16; // eax
  int v17; // esi
  _DWORD *v18; // eax
  _DWORD *v19; // eax
  char v20; // al
  _DWORD *v21; // eax
  _DWORD *v22; // eax
  _DWORD *v23; // eax
  _DWORD *v24; // eax
  _DWORD *v25; // eax
  int result; // eax
  int v27; // [esp+1Eh] [ebp-20h]
  int v28; // [esp+22h] [ebp-1Ch]
  int v29; // [esp+26h] [ebp-18h]
  int v30; // [esp+2Ah] [ebp-14h]
  _UNKNOWN *retaddr; // [esp+3Eh] [ebp+0h] BYREF

  *(_DWORD *)(a2 + 12) = dword_543E2C;
  sub_B3470("ContinueCareerNewCar", a4, 0, *a1, a1[1], a1[2], a1[3], 0, v27, v28, v29, v30);
  v12 = a4 + 1;
  v13 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_946B0, a3);
  sub_B3470(
    "ContinueCareer",
    v12,
    0,
    *v13,
    v13[1],
    v13[2],
    v13[3],
    0,
    dword_543E20,
    dword_543E24,
    dword_543E28,
    dword_543E2C);
  v14 = v12 + 1;
  if ( *(_DWORD *)(dword_3AD2F8 + 4) != 3 && !byte_3ACE91 )
  {
    v15 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_94480, a3);
    sub_B3470(
      "InstantReplay",
      v14++,
      0,
      *v15,
      v15[1],
      v15[2],
      v15[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
  }
  if ( dword_3AC6E0 != 2 && *(_DWORD *)(dword_3AD2F8 + 4) != 3 )
  {
    v16 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                      sub_95420,
                      a3,
                      0,
                      0);
    sub_B3470(
      "CM_Options",
      v14,
      0,
      *v16,
      v16[1],
      v16[2],
      v16[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
    v17 = v14 + 1;
    v18 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                      sub_95880,
                      a3,
                      0,
                      0);
    sub_B3470(
      "CM_AudioOptions",
      v17,
      0,
      *v18,
      v18[1],
      v18[2],
      v18[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
    v14 = v17 + 1;
    if ( !byte_3ACE91 && *(_DWORD *)(dword_3AD2F8 + 4) != 3 )
    {
      v19 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                        sub_979A0,
                        a3,
                        0,
                        0);
      sub_B3470(
        "CM_ChangeVehicle",
        v14++,
        0,
        *v19,
        v19[1],
        v19[2],
        v19[3],
        0,
        dword_543E20,
        dword_543E24,
        dword_543E28,
        dword_543E2C);
    }
  }
  HIBYTE(retaddr) = 1;
  if ( dword_3AC6E0 == 2 && (unsigned __int8)sub_150540(dword_3ACD38, &unk_3ACD90, &a11) )
    HIBYTE(retaddr) = dword_34F654[1182 * dword_3ACD38 + 8 * a11] == 33;
  if ( (unsigned __int8)sub_93410() )
    v20 = 0;
  else
    v20 = HIBYTE(retaddr);
  if ( dword_3AC6E0 == 2 && !*(_BYTE *)(a3 + 4) )
  {
    if ( v20 && *(_DWORD *)(dword_3AD2F8 + 4) != 3 )
    {
      v21 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                        sub_979A0,
                        a3,
                        0,
                        0);
      sub_B3470(
        "CM_ChangeVehicle",
        v14++,
        0,
        *v21,
        v21[1],
        v21[2],
        v21[3],
        0,
        dword_543E20,
        dword_543E24,
        dword_543E28,
        dword_543E2C);
    }
    if ( (unsigned __int8)sub_14F5D0((char *)&retaddr + 3)
      && dword_34FDF0[1182 * a12 + 33 * HIBYTE(retaddr)] >= 0
      && *(_DWORD *)(dword_3AD2F8 + 4) != 3 )
    {
      v22 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_93F80, a3);
      sub_B3470(
        "StartCruise",
        v14++,
        0,
        *v22,
        v22[1],
        v22[2],
        v22[3],
        0,
        dword_543E20,
        dword_543E24,
        dword_543E28,
        dword_543E2C);
    }
  }
  if ( (unsigned __int8)sub_93120() )
  {
    v23 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__Base__ptr(sub_99520, a3);
    sub_B3470(
      "PM_PlayerList",
      v14++,
      0,
      *v23,
      v23[1],
      v23[2],
      v23[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
  }
  if ( byte_3ACD71 && !byte_3ACE91 )
  {
    v24 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                      mcMenuShell__ActivateConfirmation_void,
                      a3,
                      8,
                      0);
    sub_B3470(
      "GE_EXIT_TO_RE",
      v14++,
      0,
      *v24,
      v24[1],
      v24[2],
      v24[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
  }
  if ( *(_DWORD *)(dword_3AD2F8 + 4) != 3 || dword_3AC6E0 != 2 )
  {
    v25 = (_DWORD *)datCallback__datCallback_void_Base___ptr__Base__ptr__void__ptr__Base__ptr__void__ptr__bool(
                      mcMenuShell__ActivateConfirmation_void,
                      a3,
                      7,
                      0);
    sub_B3470(
      "GE_EXIT_TO_FE",
      v14,
      0,
      *v25,
      v25[1],
      v25[2],
      v25[3],
      0,
      dword_543E20,
      dword_543E24,
      dword_543E28,
      dword_543E2C);
  }
  *(_BYTE *)(*(_DWORD *)(a3 + 76) + 1352) = 1;
  *(_BYTE *)(*(_DWORD *)(a3 + 76) + 1353) = 0;
  *(_BYTE *)(*(_DWORD *)(a3 + 76) + 1354) = 0;
  sub_B0FE0(*(_DWORD *)(a3 + 76), 1);
  result = mcPlayerManager__SetInputEnable_bool_bool(0, 0);
  *(_BYTE *)(*(_DWORD *)(a3 + 76) + 1160) = 0;
  return result;
}

```

### `mcRaceBase__LoadResetPosition_void`
- **MC2 Xbox VA:** `0x09BDA0..0x9bf8e` (496 B) | **MC3 Xbox VA:** `0x1CA6E0` (530 B, delta: `+34 B`) | **MC3 PS2 VA:** `0x3D5A30`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_0842827fa7b14458085aba67564bc92802e7bea45dbce76eae7768076dd5c0fb`

```cpp
_DWORD *__thiscall mcRaceBase__LoadResetPosition_void(_DWORD *this)
{
  int v1; // ebx
  int Data_datBinTokenizer__ref__phBound__FileVersion; // edi
  int Int_void; // ebp
  int v5; // eax
  int v6; // edi
  int v7; // edi
  double i; // st7
  int v9; // eax
  _DWORD *result; // eax
  _DWORD *v11; // eax
  _DWORD *v12; // edi
  _DWORD *v13; // esi
  int v14; // [esp+Ch] [ebp-D4h]
  _DWORD v15[3]; // [esp+10h] [ebp-D0h] BYREF
  float v16; // [esp+1Ch] [ebp-C4h]
  char v17[32]; // [esp+20h] [ebp-C0h] BYREF
  _BYTE v18[160]; // [esp+40h] [ebp-A0h] BYREF

  v1 = 0;
  Data_datBinTokenizer__ref__phBound__FileVersion = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
                                                      "tune/city",
                                                      off_34F2E4[dword_3ACD38],
                                                      "reset",
                                                      0,
                                                      1);
  v14 = Data_datBinTokenizer__ref__phBound__FileVersion;
  if ( Data_datBinTokenizer__ref__phBound__FileVersion )
  {
    datTokenizer__datTokenizer_void(v18);
    datBaseTokenizer__Init_char_const__ptr__Stream__ptr(
      off_34F2E4[dword_3ACD38],
      Data_datBinTokenizer__ref__phBound__FileVersion);
    this[519] = 0;
    Int_void = datAsciiTokenizer__GetInt_void(v18);
    this[518] = Int_void;
    v5 = sub_1789E0(16 * Int_void);
    v6 = v5;
    if ( v5 )
      swfVARIANT__asInt_void_const(v5, 16, Int_void, mcExplosionParticles__mcExplosionParticles_void);
    else
      v6 = 0;
    this[516] = v6;
    v7 = 0;
    for ( this[517] = sub_1789E0(4 * Int_void); v7 < Int_void; *(float *)(v9 + 12) = v16 )
    {
      datAsciiTokenizer__GetVector_Vector4__ref(v15);
      datBaseTokenizer__GetToken_char__ptr__int(v17, 32);
      *(_DWORD *)(this[517] + 4 * v7) = sub_1789E0(strlen(v17) + 1);
      strcpy(*(char **)(this[517] + 4 * v7), v17);
      for ( i = v16; i > 360.0; i = i - 360.0 )
        ;
      v9 = v1 + this[516];
      v16 = i * 0.017453292;
      *(_DWORD *)v9 = v15[0];
      *(_DWORD *)(v9 + 4) = v15[1];
      *(_DWORD *)(v9 + 8) = v15[2];
      ++v7;
      v1 += 16;
    }
    return (_DWORD *)Stream__Close_void(v14);
  }
  else
  {
    this[518] = 2;
    v11 = (_DWORD *)sub_1789E0(32);
    v12 = v11;
    if ( v11 )
    {
      swfVARIANT__asInt_void_const(v11, 16, 2, mcExplosionParticles__mcExplosionParticles_void);
      result = v12;
    }
    else
    {
      result = 0;
    }
    this[516] = result;
    *result = 0;
    result[1] = 0;
    result[2] = 0;
    result[3] = 0;
    v13 = (_DWORD *)(this[516] + 16);
    *v13 = 0;
    v13[1] = 0;
    v13[2] = 0;
    v13[3] = 0;
  }
  return result;
}

```

### `mcRaceBase__LoadWeather_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x09BF90..0x9c102` (384 B) | **MC3 Xbox VA:** `0x1CA900` (228 B, delta: `-156 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_81988e2b89a3bf09b1051e67a7b136e087747f4138c315a01a3db294a7dcab8c`

```cpp
char __stdcall mcRaceBase__LoadWeather_datAsciiTokenizer__ref(int a1)
{
  int v2; // eax
  int v3; // ebx
  int v4; // eax
  int v5; // edi
  float v7; // [esp+4h] [ebp-34h] BYREF
  float v8; // [esp+8h] [ebp-30h] BYREF
  _DWORD v9[2]; // [esp+Ch] [ebp-2Ch] BYREF
  int v10[3]; // [esp+14h] [ebp-24h] BYREF
  int v11[3]; // [esp+20h] [ebp-18h] BYREF
  _BYTE v12[12]; // [esp+2Ch] [ebp-Ch] BYREF
  int v13; // [esp+3Ch] [ebp+4h]

  sub_123410();
  v2 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
  if ( v2 > 0 )
  {
    v3 = v2;
    do
    {
      datBaseTokenizer__MatchIToken_char_const__ptr("Weather");
      datBaseTokenizer__MatchToken_char_const__ptr("{");
      datBaseTokenizer__MatchToken_char_const__ptr("Properties");
      if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Fog", 1) )
      {
        (*(void (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
        datBaseTokenizer__MatchToken_char_const__ptr("Ellipse");
        (*(void (__thiscall **)(int, int *))(*(_DWORD *)a1 + 36))(a1, v11);
        (*(void (__thiscall **)(int, _BYTE *))(*(_DWORD *)a1 + 36))(a1, v12);
        (*(void (__thiscall **)(int, _DWORD *))(*(_DWORD *)a1 + 40))(a1, v9);
        datBaseTokenizer__MatchToken_char_const__ptr("}");
        v4 = _builtin_new(7864);
        if ( v4 )
          v5 = sub_120BA0(v4);
        else
          v5 = 0;
        v10[0] = v9[0];
        v10[1] = 1084227584;
        v10[2] = v9[1];
        sub_120340(0, (int)v11, (int)v10, 0.0);
        sub_120970(v5);
      }
      else if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Rain", 1) )
      {
        v13 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
        datBaseTokenizer__MatchToken_char_const__ptr("Circle");
        (*(void (__thiscall **)(int, int *))(*(_DWORD *)a1 + 36))(a1, v11);
        v8 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a1 + 20))(a1);
        datBaseTokenizer__MatchToken_char_const__ptr("}");
        v7 = (double)v13 * 0.0099999998;
        sub_123420(v11, &v8, &v7);
      }
      --v3;
    }
    while ( v3 );
  }
  return 1;
}

```

### `mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x09C3F0..0x9c532` (336 B) | **MC3 Xbox VA:** `0x1CAEF0` (331 B, delta: `-5 B`) | **MC3 PS2 VA:** `0x3D7960`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_fab797e4af011c0fa6bce0cfdd538c5530b81538eafedb762d37ea28165e9880`

```cpp
char __thiscall mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref(_DWORD *this, int a2, int a3)
{
  float *v3; // edi

  v3 = (float *)(this[7] + 124 * a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumCarAiInfo", 1)
    && (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) )
  {
    datBaseTokenizer__MatchIToken_char_const__ptr("CarAiInfo");
    datBaseTokenizer__MatchIToken_char_const__ptr("{");
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("TurnConst", 1) )
      v3[23] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("HandbrakeEarlyTime", 1) )
      v3[24] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("HandbrakeSteerMultiplier", 1) )
      v3[25] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("MaxBrakeDeceleration", 1) )
      v3[26] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("SteerScalar", 1) )
      v3[27] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CarFrictionHandling", 1) )
      v3[28] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("FrictionMultiplier", 1) )
      v3[29] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("SlidingFrictionFactor", 1) )
      v3[30] = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    datBaseTokenizer__MatchIToken_char_const__ptr("}");
  }
  return 1;
}

```

### `mcRaceBase__LoadOpponentPersonality_int_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x09C540..0x9c733` (512 B) | **MC3 Xbox VA:** `0x1CB040` (523 B, delta: `+11 B`) | **MC3 PS2 VA:** `0x3D7B80`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_3a3b8e6dba07e9939defeb75bb6eded208ff17f909f57baae83b533511449ca4`

```cpp
char __thiscall mcRaceBase__LoadOpponentPersonality_int_datAsciiTokenizer__ref(_DWORD *this, int a2, int a3)
{
  int v4; // ebp
  int v6; // edi

  datBaseTokenizer__MatchIToken_char_const__ptr("numPersonality");
  v4 = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
  if ( !v4 )
    return 0;
  datBaseTokenizer__MatchIToken_char_const__ptr("Personality");
  datBaseTokenizer__MatchToken_char_const__ptr("{");
  v6 = 0;
  while ( v6 < v4 )
  {
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("AvoidSST", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 75) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseSST", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 76) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RamsPlayer", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 72) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("FishtailPlayer", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 73) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("BlockPlayer", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 74) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("AttackCops", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 78) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseBadPowerups", 1) )
    {
      (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseNitro", 1) )
    {
      (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseGoodPowerups", 1) )
    {
      (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseBurnoutStart", 1) )
    {
      *(_BYTE *)(124 * a2 + this[7] + 81) = -4;
      (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
      ++v6;
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("UseEarlyStart", 1) )
    {
      ++v6;
      *(float *)(124 * a2 + this[7] + 84) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    }
  }
  datBaseTokenizer__MatchToken_char_const__ptr("}");
  return 1;
}

```

### `mcRaceBase__LoadAmbientRoadOverride_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x09C830..0x9c980` (336 B) | **MC3 Xbox VA:** `0x1CB380` (334 B, delta: `-2 B`) | **MC3 PS2 VA:** `0x3D8820`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_a7ff9b6de52ca7757011d075340f337dc62d952be8b172feee3cd65ca483ed9e`

```cpp
char __stdcall mcRaceBase__LoadAmbientRoadOverride_datAsciiTokenizer__ref(int a1)
{
  int v2; // ebp
  int v3; // edi
  char v4; // bl
  int v5; // edi
  int Road_int_const; // ebp
  double v7; // st7
  float v9; // [esp+0h] [ebp-38h]
  float v10; // [esp+14h] [ebp-24h]
  float v11; // [esp+18h] [ebp-20h]
  float v12; // [esp+1Ch] [ebp-1Ch]
  int v13; // [esp+20h] [ebp-18h]
  _DWORD v14[5]; // [esp+24h] [ebp-14h]
  bool v15; // [esp+3Ch] [ebp+4h]

  v2 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
  if ( v2 )
  {
    v3 = dword_3ACD44;
    v4 = 0;
    v14[0] = 0;
    v14[1] = 1056964608;
    v14[2] = 1065353216;
    v14[3] = 1069547520;
    v14[4] = 1065353216;
    v15 = 1;
    v10 = 5.0;
    v12 = 1.0;
    if ( dword_3ACD44 != 4 )
    {
      v15 = dword_3ACD44 != 0;
      v4 = 1;
      v10 = mc__ConvertTrafficDensityEnumToFloat_mc__eTrafficDensity(dword_3ACD44);
      v12 = *(float *)&v14[v3];
    }
    datBaseTokenizer__MatchIToken_char_const__ptr("AmbientRoads");
    datBaseTokenizer__MatchToken_char_const__ptr("{");
    if ( v2 > 0 )
    {
      v13 = v2;
      do
      {
        v5 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
        if ( v15 )
        {
          Road_int_const = aiRailNetwork__GetRoad_int_const(v5);
          v7 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a1 + 20))(a1);
          v9 = v7;
          sub_1507E0(v9);
          v11 = v7 * v12;
          if ( v4 && v11 > (double)v10 )
            v11 = v10;
          if ( (*(_BYTE *)(Road_int_const + 6) & 6) == 0 )
          {
            aiRailNetwork__GetRoad_int_const(v5);
            sub_116D20(LODWORD(v11));
          }
        }
        else
        {
          (*(void (__thiscall **)(int))(*(_DWORD *)a1 + 20))(a1);
        }
        --v13;
      }
      while ( v13 );
    }
    datBaseTokenizer__MatchToken_char_const__ptr("}");
  }
  return 1;
}

```

### `mcRaceBase__LoadClosedRoads_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x09C980..0x9ca0d` (144 B) | **MC3 Xbox VA:** `0x1CB4D0` (126 B, delta: `-18 B`) | **MC3 PS2 VA:** `0x3D89F0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_8df1e9a741bdda34e15eadf61d161c1417833f036b3096fc78bc28c59631228c`

```cpp
char __stdcall mcRaceBase__LoadClosedRoads_datAsciiTokenizer__ref(int a1)
{
  int v1; // ebx
  int v2; // esi

  v1 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
  if ( v1 )
  {
    datBaseTokenizer__MatchIToken_char_const__ptr("ClosedRoads");
    datBaseTokenizer__MatchToken_char_const__ptr("{");
    if ( v1 > 0 )
    {
      do
      {
        v2 = (*(int (__thiscall **)(int))(*(_DWORD *)a1 + 16))(a1);
        aiRailNetwork__GetRoad_int_const(v2);
        aiRoad__SetFlag_unsigned_int(2);
        aiRailNetwork__GetRoad_int_const(v2);
        sub_116D20(0);
        --v1;
        *(_DWORD *)(aiRailNetwork__GetRoad_int_const(v2) + 48) = 0;
      }
      while ( v1 );
    }
    datBaseTokenizer__MatchToken_char_const__ptr("}");
  }
  return 1;
}

```

### `mcRaceOver__CheckAndShowUnlockedCar_void`
- **MC2 Xbox VA:** `0x09DAE0..0x9dc53` (384 B) | **MC3 Xbox VA:** `0x1A1760` (416 B, delta: `+32 B`) | **MC3 PS2 VA:** `0x3DDA08`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_63bca9634e34e78da35c3e6160dd44f657da488e18b4efe0598639d27e3c5c54`

```cpp
int __thiscall mcRaceOver__CheckAndShowUnlockedCar_void(_DWORD *this)
{
  int v2; // edi
  int v3; // ebx
  int v4; // esi
  int v5; // edi
  int v6; // ecx
  __int64 IsVehicleUnlocked_int_const; // rax
  int v8; // ebx
  int char_const__ptr; // eax
  int v10; // eax
  int v11; // eax
  int v13; // [esp+10h] [ebp-58h]
  int v14; // [esp+14h] [ebp-54h]
  _BYTE v15[80]; // [esp+18h] [ebp-50h] BYREF

  v2 = dword_3AD300;
  mcConfig__GetPlayer_int(byte_3ACE91 != 0 ? dword_3ACE94 : 0);
  v3 = this[512];
  v14 = this[513];
  IsVehicleUnlocked_int_const = mcUnlocking__IsVehicleUnlocked_int_const(v2 + 84);
  v4 = v3 ^ IsVehicleUnlocked_int_const;
  v5 = v14 ^ HIDWORD(IsVehicleUnlocked_int_const);
  v6 = 0;
  HIDWORD(IsVehicleUnlocked_int_const) = v3 ^ IsVehicleUnlocked_int_const;
  v8 = 0;
  v13 = 0;
  v14 = 0;
  if ( !(v5 | HIDWORD(IsVehicleUnlocked_int_const)) )
    goto LABEL_9;
  do
  {
    if ( v5 & (1 << v6 >> 31) | v4 & (1 << v6) )
      *(&v13 + v8++) = v6;
    ++v6;
  }
  while ( v6 < 32 );
  if ( v8 > 0 )
  {
    *(_BYTE *)(dword_3813E0 + 252) = v13;
    char_const__ptr = txtStringTable__Get_char_const__ptr("you_unlock_car");
    sub_B9680(20, *(_DWORD *)(char_const__ptr + 8));
    sub_B8670(20);
    strlen(v15, 80, "SS_%s", off_34F338[v13]);
    v10 = txtStringTable__Get_char_const__ptr(v15);
    sub_B9680(19, *(_DWORD *)(v10 + 8));
    sub_B8670(19);
    if ( v8 == 2 )
    {
      strlen(v15, 80, "SS_%s", off_34F338[v14]);
      v11 = txtStringTable__Get_char_const__ptr(v15);
      sub_B9680(21, *(_DWORD *)(v11 + 8));
      sub_B8670(21);
    }
  }
  LODWORD(IsVehicleUnlocked_int_const) = v13;
  if ( !v13 )
LABEL_9:
    *(_BYTE *)(dword_3813E0 + 252) = 0;
  return IsVehicleUnlocked_int_const;
}

```

### `mcRaceOver__CheckAndShowUnlockedAbilities_void`
- **MC2 Xbox VA:** `0x09DC60..0x9dda3` (336 B) | **MC3 Xbox VA:** `0x1A1760` (416 B, delta: `+80 B`) | **MC3 PS2 VA:** `0x3DDA08`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_1ae324f59cf8b942cf6cbe0e7591035a8e7828a54b962f3fad9fc8389c71a2c6`

```cpp
void __thiscall mcRaceOver__CheckAndShowUnlockedAbilities_void(_BYTE *this)
{
  int v2; // edi
  int v3; // eax
  int char_const__ptr; // eax
  int v5; // [esp-Ch] [ebp-10h]
  int v6; // [esp-Ch] [ebp-10h]
  int v7; // [esp-Ch] [ebp-10h]

  if ( dword_3AC6E0 == 2 )
  {
    mcConfig__GetPlayer_int(byte_3ACE91 != 0 ? dword_3ACE94 : 0);
    v2 = dword_3AD300 + 84;
    if ( !this[2057] && (unsigned __int8)mcUnlocking__IsBurnoutUnlocked_bool_const(1) )
    {
      v5 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("Unlock_Slipstream") + 8);
      sub_B9680(19, v5);
LABEL_18:
      char_const__ptr = txtStringTable__Get_char_const__ptr("you_unlock_ability");
      sub_B9680(20, *(_DWORD *)(char_const__ptr + 8));
      sub_B8670(20);
      sub_B8670(19);
      return;
    }
    if ( !this[2058] && (unsigned __int8)mcUnlocking__IsTwoWheelDrivingUnlocked_bool_const(1) )
    {
      v3 = txtStringTable__Get_char_const__ptr("Unlock_Burnout");
LABEL_17:
      sub_B9680(19, *(_DWORD *)(v3 + 8));
      goto LABEL_18;
    }
    if ( !this[2060] && (unsigned __int8)mcUnlocking__IsInAirControlUnlocked_bool_const(1) )
    {
      v6 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("Unlock_InAirControls") + 8);
      sub_B9680(19, v6);
      goto LABEL_18;
    }
    if ( !this[2059] && (unsigned __int8)mcUnlocking__IsSlipstreamTurboUnlocked_bool_const(1) )
    {
      v7 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("Unlock_TwoWheelDriving") + 8);
      sub_B9680(19, v7);
      goto LABEL_18;
    }
    if ( !this[2056] && (unsigned __int8)mcUnlocking__IsNitroUnlockedForPlayer_void_const(v2) )
    {
      v3 = txtStringTable__Get_char_const__ptr("Unlock_Nitro");
      goto LABEL_17;
    }
  }
}

```

### `mcRaceBase__LoadOpponents_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x0A26A0..0xa2cb0` (1552 B) | **MC3 Xbox VA:** `0x1D3AE0` (2116 B, delta: `+564 B`) | **MC3 PS2 VA:** `0x3D6ED8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_f13e270966ad5cfec15a9c1a4feebe75c12be7afa6e826c08fbf31341b0a8d58`

```cpp
char __thiscall mcRaceBase__LoadOpponents_datAsciiTokenizer__ref(_DWORD *this, int a2)
{
  int v3; // ebp
  int *v4; // eax
  int v5; // ebp
  _DWORD *v6; // ebx
  _DWORD *v7; // ecx
  int v8; // ebp
  int v9; // ecx
  int v10; // ebp
  int v11; // eax
  int v12; // ebp
  int v13; // ebx
  int v14; // ebp
  int v15; // ebx
  int v16; // ebp
  long double v17; // st7
  int v18; // edx
  long double v19; // st6
  int v20; // eax
  double v21; // st5
  int v22; // eax
  int v23; // eax
  int v24; // ebx
  int v25; // ebx
  int v26; // eax
  int i; // esi
  int v28; // eax
  int v30; // [esp+10h] [ebp-A0h]
  int v31; // [esp+10h] [ebp-A0h]
  int v32; // [esp+14h] [ebp-9Ch] BYREF
  _DWORD v33[3]; // [esp+18h] [ebp-98h] BYREF
  float v34[3]; // [esp+24h] [ebp-8Ch] BYREF
  _BYTE v35[128]; // [esp+30h] [ebp-80h] BYREF

  v3 = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
  this[3] = v3;
  this[4] = v3;
  v4 = (int *)sub_1789E0(124 * v3 + 4);
  if ( v4 )
  {
    *v4 = v3;
    v5 = v3 - 1;
    v6 = v4 + 1;
    v7 = v4 + 1;
    if ( v5 >= 0 )
    {
      v8 = v5 + 1;
      do
      {
        sub_9E4F0(v7);
        v7 = (_DWORD *)(v9 + 124);
        --v8;
      }
      while ( v8 );
    }
  }
  else
  {
    v6 = 0;
  }
  v10 = this[3];
  this[7] = v6;
  v11 = sub_1789E0(76 * v10);
  v30 = v11;
  if ( v11 )
  {
    v12 = v10 - 1;
    v13 = v11;
    if ( v12 >= 0 )
    {
      v14 = v12 + 1;
      do
      {
        sub_A1C80(v13);
        v13 += 76;
        --v14;
      }
      while ( v14 );
      v11 = v30;
    }
  }
  else
  {
    v11 = 0;
  }
  this[354] = v11;
  v15 = 0;
  v31 = 0;
  if ( (int)this[3] > 0 )
  {
    v16 = 0;
    do
    {
      datBaseTokenizer__MatchIToken_char_const__ptr("opponent");
      datBaseTokenizer__MatchToken_char_const__ptr("{");
      datBaseTokenizer__MatchIToken_char_const__ptr("cartype");
      (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v35, 128);
      *(_BYTE *)(this[7] + v16) = mc__LookupCar_char_const__ptr(v35);
      datBaseTokenizer__MatchIToken_char_const__ptr("posdir");
      (*(void (__thiscall **)(int, _DWORD *))(*(_DWORD *)a2 + 36))(a2, v33);
      (*(void (__thiscall **)(int, float *))(*(_DWORD *)a2 + 36))(a2, v34);
      v17 = -v34[2];
      v18 = v33[0];
      v19 = -v34[0];
      v20 = this[7] + v16 + 48;
      v21 = *(float *)&v33[2];
      *(float *)(v20 + 4) = *(float *)&v33[1];
      *(_DWORD *)v20 = v18;
      *(float *)(v20 + 8) = v21;
      *(float *)(v20 + 12) = atan2(v19, v17);
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("DisabledAtStart", 1) )
        *(_BYTE *)(this[7] + v16 + 2) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) <= 0;
      else
        *(_BYTE *)(this[7] + v16 + 2) = 1;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RemoveAtEnd", 1) )
        (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RespawnCop", 1) )
        *(_BYTE *)(this[7] + v16 + 3) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 3) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CopBehaveRam", 1) )
        *(_BYTE *)(this[7] + v16 + 5) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 5) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CopBehaveNudge", 1) )
        *(_BYTE *)(this[7] + v16 + 6) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 6) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CopBehaveBlock", 1) )
        *(_BYTE *)(this[7] + v16 + 7) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 7) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CopBehaveAlongside", 1) )
        *(_BYTE *)(this[7] + v16 + 8) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 8) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("AttackPlayersOnly", 1) )
        *(_BYTE *)(this[7] + v16 + 4) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) != 0;
      else
        *(_BYTE *)(this[7] + v16 + 4) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("InitialSpeed", 1) )
        *(float *)(this[7] + v16 + 16) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2) * 0.44703999;
      else
        *(_DWORD *)(this[7] + v16 + 16) = 0;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NonCompetitorAI", 1) )
        *(_BYTE *)(this[7] + v16 + 10) = 0;
      else
        *(_BYTE *)(this[7] + v16 + 10) = 1;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("ThrottleLimit", 1) )
        *(float *)(this[7] + v16 + 12) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
      else
        *(_DWORD *)(this[7] + v16 + 12) = 1065353216;
      if ( (unsigned __int8)sub_150980(*(char *)(this[7] + v16)) )
        *(_BYTE *)(this[7] + v16 + 1) = 2;
      else
        *(_BYTE *)(this[7] + v16 + 1) = 0;
      if ( _builtin_new(48) )
        v22 = sub_C5690(0);
      else
        v22 = 0;
      *(_DWORD *)(this[7] + v16 + 64) = v22;
      if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumUsedRubberBand", 1)
        && (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) )
      {
        datBaseTokenizer__MatchIToken_char_const__ptr("RubberBand");
        datBaseTokenizer__MatchIToken_char_const__ptr("{");
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandMinDist", 1) )
          *(float *)(this[7] + v16 + 20) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandMaxDist", 1) )
          *(float *)(this[7] + v16 + 24) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandMinThrottle", 1) )
          *(float *)(this[7] + v16 + 28) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandBehindMaxThrottle", 1) )
          *(float *)(this[7] + v16 + 44) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandMinSpeed", 1) )
          *(float *)(this[7] + v16 + 32) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2)
                                         * 0.44703999;
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandBehindMinDist", 1) )
          *(float *)(this[7] + v16 + 36) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RubberBandBehindMaxDist", 1) )
          *(float *)(this[7] + v16 + 40) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
        datBaseTokenizer__MatchIToken_char_const__ptr("}");
      }
      if ( dword_3ACD54 )
      {
        *(_BYTE *)(this[7] + v16 + 79) = -5;
        *(_BYTE *)(this[7] + v16 + 80) = -5;
        *(_BYTE *)(this[7] + v16 + 77) = -4;
      }
      mcRaceBase__LoadOpponentPersonality_int_datAsciiTokenizer__ref(this, v15, a2);
      mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref(this, v15, a2);
      datBaseTokenizer__MatchIToken_char_const__ptr("Route");
      datBaseTokenizer__MatchToken_char_const__ptr("{");
      aiPathGraph__Load_datAsciiTokenizer__ref__mcRaceBase__ptr(a2, this);
      datBaseTokenizer__MatchToken_char_const__ptr("}");
      aiOpponentStart__LoadPreRacePath_datAsciiTokenizer__ref(a2);
      datBaseTokenizer__MatchToken_char_const__ptr("}");
      if ( !dword_3ACD4C )
      {
        v23 = this[7] + v16;
        if ( *(_BYTE *)(v23 + 1) == 2 )
        {
          v24 = *(_DWORD *)(v23 + 64);
          if ( v24 )
          {
            sub_C56D0(*(_DWORD *)(v23 + 64));
            _builtin_delete(v24);
          }
          *(_DWORD *)(this[7] + v16 + 64) = 0;
          v16 -= 124;
          --this[3];
          v15 = v31 - 1;
        }
      }
      ++v15;
      v16 += 124;
      v31 = v15;
    }
    while ( v15 < this[3] );
  }
  v25 = 0;
  v32 = 11;
  sub_207FE0("maxopponents", 0, &v32);
  v26 = this[3];
  if ( v26 >= v32 )
    v26 = v32;
  this[3] = v26;
  if ( v26 >= dword_3ACD6C )
    v26 = dword_3ACD6C;
  this[3] = v26;
  if ( !byte_3ACE9B )
    this[3] = 0;
  for ( i = 0; i < this[3]; v25 += 124 )
  {
    v28 = sub_14E9C0(i);
    if ( v28 != 33 )
      *(_BYTE *)(v25 + this[7]) = v28;
    ++i;
  }
  return 1;
}

```

### `mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x0A34F0..0xa379d` (475 B) | **MC3 Xbox VA:** `0x1D4F20` (2832 B, delta: `+2357 B`) | **MC3 PS2 VA:** `0x3D4A20`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_e4723492d366040052b9a0ce0ccd2ec17a5e45c3eb14d8308146df2a057c96a2`

```cpp
int __userpurge mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref@<eax>(
        int a1@<ecx>,
        double a2@<st0>,
        int a3,
        int a4)
{
  int v5; // eax
  int v6; // eax
  double v7; // st7
  char v8; // al
  int v9; // ebx
  float v11; // [esp+0h] [ebp-FCh]
  float v12; // [esp+0h] [ebp-FCh]
  _BYTE v13[8]; // [esp+74h] [ebp-88h] BYREF
  _BYTE v14[112]; // [esp+7Ch] [ebp-80h] BYREF
  int v15; // [esp+ECh] [ebp-10h]

  *(_DWORD *)(a1 + 1508) = 1;
  datBaseTokenizer__MatchIToken_char_const__ptr("racetype");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a3 + 4))(a3, v14, 128);
  *(_DWORD *)(a1 + 8) = mc__LookupRaceType_char_const__ptr(v13);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RaceStartTime", 1) )
  {
    a2 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    *(float *)(a1 + 1512) = a2;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("ActualHookman", 1) )
  {
    v5 = sub_1789E0(32);
    *(_DWORD *)(a1 + 1524) = v5;
    (*(void (__thiscall **)(int, int, int))(*(_DWORD *)a3 + 4))(a3, v5, 31);
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("BreakinHookman", 1) )
  {
    v6 = sub_1789E0(32);
    *(_DWORD *)(a1 + 1528) = v6;
    (*(void (__thiscall **)(int, int, int))(*(_DWORD *)a3 + 4))(a3, v6, 31);
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumOfLaps", 1) )
    *(_DWORD *)(a1 + 1508) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RaceDensity", 1) )
  {
    v7 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    v11 = v7;
    sub_1507E0(v11);
    *(float *)(a1 + 1516) = v7;
    a2 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
    v12 = a2;
    sub_1507E0(v12);
    *(float *)(a1 + 1520) = a2;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RacePreAudio", 1) )
  {
    *(_BYTE *)(a1 + 1532) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1533) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1534) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1535) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1536) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1537) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("RaceDurAudio", 1) )
  {
    *(_BYTE *)(a1 + 1538) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1539) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1540) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1541) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1542) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1543) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
    *(_BYTE *)(a1 + 1544) = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 16))(a3) != 0;
  }
  v8 = datBaseTokenizer__CheckIToken_char_const__ptr__bool("BeforeCountDownLength", 1);
  v9 = v15;
  if ( v8 )
  {
    (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 20))(a3);
    if ( !v9 )
      *(float *)(dword_3AD30C + 24) = a2;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CountDownLength", 1) )
  {
    (*(void (__thiscall **)(int))(*(_DWORD *)a3 + 20))(a3);
    if ( !v9 )
      *(float *)(dword_3AD30C + 28) = a2;
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("FinishedLength", 1) )
    *(float *)(dword_3AD30C + 32) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
  return mcRaceBase__Load_datAsciiTokenizer__ref__mcRaceBase__ptr(a3, a4);
}

```

### `mcRaceBase__Load_datAsciiTokenizer__ref__mcRaceBase__ptr`
- **MC2 Xbox VA:** `0x0A379D..0xa3d98` (1539 B) | **MC3 Xbox VA:** `0x1D4F20` (2818 B, delta: `+1279 B`) | **MC3 PS2 VA:** `0x3D4A20`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_2c2f3ade95c2373c7f01f3e77899dd933ac44ccd751f26b93242542abcd260b2`

```cpp
// positive sp value has been detected, the output may be wrong!
char __userpurge mcRaceBase__Load_datAsciiTokenizer__ref__mcRaceBase__ptr@<al>(
        int a1@<ebx>,
        int a2@<edi>,
        int a3@<esi>,
        char a4,
        int a5)
{
  char v5; // bl
  double v6; // st7
  double v7; // st6
  double v8; // st5
  int v9; // eax
  char v11; // [esp-BFh] [ebp-D3h]
  char v12; // [esp-BDh] [ebp-D1h]
  int v13; // [esp-BCh] [ebp-D0h]
  float v14; // [esp-B0h] [ebp-C4h]
  char v15; // [esp-ACh] [ebp-C0h]
  char v16; // [esp-A4h] [ebp-B8h]
  int v17; // [esp-A4h] [ebp-B8h]
  char v18; // [esp-A0h] [ebp-B4h]
  int v19; // [esp-A0h] [ebp-B4h]
  float v20; // [esp-9Ch] [ebp-B0h]
  int v21; // [esp-98h] [ebp-ACh]
  int v22; // [esp-94h] [ebp-A8h]
  int v23; // [esp-8Ch] [ebp-A0h]
  int v24; // [esp-88h] [ebp-9Ch]
  float v25; // [esp-84h] [ebp-98h]
  float v26; // [esp-7Ch] [ebp-90h]
  int v27; // [esp-78h] [ebp-8Ch] BYREF
  int v28; // [esp-74h] [ebp-88h] BYREF
  int v29; // [esp-70h] [ebp-84h]
  _DWORD v30[5]; // [esp-6Ch] [ebp-80h] BYREF
  _DWORD v31[22]; // [esp-58h] [ebp-6Ch] BYREF

  *(_BYTE *)(dword_3AD30C + 36) = (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool(
                                                     "DontShowCountdown",
                                                     v15) == 0;
  *(_BYTE *)(dword_3AD30C + 37) = datBaseTokenizer__CheckIToken_char_const__ptr__bool("AudioDelayCountdown", 1);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CameraTransition", 1) )
  {
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("EndOfPreRaceCamera", 1) )
    {
      *(_DWORD *)(a2 + 2044) = 0;
    }
    else if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("CountDownStart", 1) )
    {
      *(_DWORD *)(a2 + 2044) = 1;
    }
    else
    {
      if ( !(unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("Go", 1) )
        ((void (__cdecl __noreturn *)(const char *))strcmp)("mcRaceBase::Load , Illegal Token for CameraTransition time");
      *(_DWORD *)(a2 + 2044) = 2;
    }
  }
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("FollowMaxDistance", 1) )
    *(float *)(a2 + 1548) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("FollowCountdown", 1) )
    *(float *)(a2 + 1552) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a3 + 20))(a3);
  if ( dword_3ACD50 && dword_3AC6E0 != 2 )
    ((void (__thiscall *)(int))sub_1511E0)(dword_3AD30C);
  if ( !a1 )
    (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 100))(a2);
  (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 96))(a2);
  BYTE1(v20) = 0;
  v22 = 0;
  v21 = 0;
  HIBYTE(v20) = 0;
  BYTE2(v20) = 0;
  v27 = dword_543A88;
  v28 = dword_543A8C;
  v29 = dword_543A90;
  v31[1] = dword_543A88;
  v31[2] = dword_543A8C;
  v31[3] = dword_543A90;
  v30[0] = dword_543A88;
  v30[1] = dword_543A8C;
  v30[2] = dword_543A90;
  v30[3] = dword_543A88;
  v30[4] = dword_543A8C;
  v31[0] = dword_543A90;
  while ( 1 )
  {
    do
    {
      while ( 1 )
      {
        v5 = 0;
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numopponents", 1) )
        {
          LOBYTE(v21) = mcRaceBase__LoadOpponents_datAsciiTokenizer__ref((_DWORD *)a2, a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numHelicopters", 1) )
        {
          sub_9C2E0(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numcheckpoints", 1) )
        {
          BYTE1(v20) = mcRaceBase__LoadCheckpoints_datAsciiTokenizer__ref(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numBangers", 1) )
        {
          BYTE1(v22) = sub_9C110(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numControlledAmbients", 1) )
        {
          LOBYTE(v22) = sub_A3010(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("PlayerPosDir", 1) )
        {
          (*(void (__thiscall **)(int, int *))(*(_DWORD *)a3 + 36))(a3, &v27);
          (*(void (__thiscall **)(int, _DWORD *))(*(_DWORD *)a3 + 36))(a3, v31);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("MultiPlayer", 1) )
        {
          datBaseTokenizer__MatchIToken_char_const__ptr("{");
          datBaseTokenizer__MatchIToken_char_const__ptr("PosDir");
          (*(void (__thiscall **)(int, int *))(*(_DWORD *)a3 + 36))(a3, &v28);
          (*(void (__thiscall **)(int, _DWORD *))(*(_DWORD *)a3 + 36))(a3, v30);
          datBaseTokenizer__MatchIToken_char_const__ptr("}");
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumShortcut", 1) )
        {
          sub_9ED50(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumTriggers", 1) )
        {
          v13 = a3;
          (*(void (__thiscall **)(int))(*(_DWORD *)(a2 + 76) + 16))(a2 + 76);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumTimerTriggers", 1) )
        {
          (*(void (__thiscall **)(int, int))(*(_DWORD *)(a2 + 76) + 20))(a2 + 76, a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numWeatherNodes", 1) )
        {
          mcRaceBase__LoadWeather_datAsciiTokenizer__ref(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumAmbientRoads", 1) )
        {
          mcRaceBase__LoadAmbientRoadOverride_datAsciiTokenizer__ref(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumPedestrianRoads", 1) )
          ((void (__cdecl __noreturn *)(const char *))strcmp)("Pedestrian Roads are not supported");
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumClosedRoads", 1) )
        {
          mcRaceBase__LoadClosedRoads_datAsciiTokenizer__ref(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumPowerUps", 1) )
        {
          if ( dword_3ACD74 != 2 || *(_DWORD *)(a2 + 12) || byte_3ACE91 || (v16 = 1, *(_DWORD *)(a2 + 8) != 10) )
            v16 = 0;
          if ( *(_BYTE *)(a2 + 2056) || (v18 = 0, byte_3ACE91) )
            v18 = 1;
          (*(void (__thiscall **)(int, int, char, char))(*(_DWORD *)(a2 + 112) + 24))(a2 + 112, a3, v16, v18);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numControlledPeds", 1) )
        {
          datBaseTokenizer__SkipToEndOfLine_void(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("NumPreRaceCameras", 1) )
        {
          sub_A32A0(a3);
          v5 = 1;
        }
        if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numSounds", 1) )
        {
          sub_A2CB0(a3);
          v5 = 1;
        }
        if ( !(unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("numAutoCopNodes", 1) )
          break;
        sub_9CB90(a3);
      }
    }
    while ( v5 );
    if ( (_BYTE)v13 && v11 && v12 && BYTE1(v13) )
      break;
    (*(void (__thiscall **)(int, _DWORD *, int))(*(_DWORD *)a3 + 4))(a3, v30, 128);
  }
  if ( HIBYTE(v13) && dword_3ACD74 > 1 )
  {
    v6 = 0.0;
    v7 = v25;
    v8 = v26;
    v17 = v23;
    v19 = v24;
  }
  else
  {
    v6 = v20;
    v7 = *(float *)&v27;
    v8 = *(float *)&v29;
    v17 = v21;
    v19 = v22;
  }
  v14 = atan2(-v7, -v8);
  if ( a5 )
    v9 = *(_DWORD *)(a5 + 2064);
  else
    v9 = *(_DWORD *)(a2 + 2064);
  *(_DWORD *)(v9 + 4) = v17;
  *(_DWORD *)(v9 + 8) = v19;
  *(float *)(v9 + 12) = v14;
  *(float *)v9 = v6;
  ((void (__thiscall *)(int))sub_12BC70)(a2 + 76);
  return 1;
}

```

### `mcRaceCheckpoint__PlayerFinished_int`
- **MC2 Xbox VA:** `0x0A43F0..0xa4837` (1104 B) | **MC3 Xbox VA:** `0x1E06E0` (1585 B, delta: `+481 B`) | **MC3 PS2 VA:** `0x3F4D60`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_c5d3472526148ef4a38d89d8a09915dbd2f569d3f123dfe61ffa2c7083eef076`

```cpp
char __thiscall mcRaceCheckpoint__PlayerFinished_int(_DWORD *this, int a2)
{
  _DWORD *v4; // esi
  char result; // al
  int v6; // ecx
  int v7; // eax
  int v8; // esi
  _DWORD *v9; // edx
  bool v10; // zf
  int v11; // ecx
  int char_const__ptr; // eax
  int v13; // eax
  _DWORD *v14; // ebx
  int v15; // edi
  int v16; // eax
  int v17; // esi
  int v18; // esi
  int v19; // eax
  int v20; // [esp-4h] [ebp-98h]
  int v21; // [esp-4h] [ebp-98h]
  int v22; // [esp-4h] [ebp-98h]
  int v23; // [esp-4h] [ebp-98h]
  char v24[12]; // [esp+0h] [ebp-94h] BYREF
  _BYTE v25[128]; // [esp+Ch] [ebp-88h] BYREF
  int v26; // [esp+8Ch] [ebp-8h]
  _DWORD *v27; // [esp+90h] [ebp-4h]
  int v28; // [esp+9Ch] [ebp+8h]
  char v29; // [esp+9Fh] [ebp+Bh]

  this[1124] |= 1 << a2;
  if ( *(_DWORD *)(dword_37FFE4 + 4 * a2 + 8) )
  {
    mcConfig__GetPlayer_int(a2);
    sub_E9A80(3);
  }
  v4 = &this[40 * a2];
  result = *((_BYTE *)v4 + 140);
  v27 = v4;
  if ( !result )
  {
    v6 = this[1122] + 1;
    this[1122] = v6;
    v28 = v6;
    if ( *(_DWORD *)(dword_3AD2F8 + 4) != 3 )
    {
      if ( (unsigned __int8)sub_A3EC0(a2) || *((float *)v4 + 36) != 0.0 )
        goto LABEL_22;
      v7 = *(_DWORD *)(dword_3AD31C + 8);
      if ( v7 < 0 )
      {
        v8 = 7;
        if ( v28 == dword_3ACD74 )
          goto LABEL_13;
      }
      else if ( this[1124] == *(_DWORD *)(dword_3AD31C + 16) )
      {
        v8 = 7;
        goto LABEL_13;
      }
      v8 = 6;
LABEL_13:
      if ( v7 < 0 )
      {
        if ( *(_DWORD *)(dword_3AD30C + 4) != 7 )
          (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD30C + 4))(dword_3AD30C, v8);
      }
      else
      {
        if ( (unsigned __int8)sub_A3EA0(this) || (unsigned __int8)sub_A3E80() )
          v10 = a2 == dword_3ACE94;
        else
          v10 = v9[2] == 0;
        if ( v10 )
          (*(void (__thiscall **)(_DWORD *, int))(*v9 + 328))(v9, v8);
      }
LABEL_22:
      if ( byte_3ACE91 )
      {
        v29 = 0;
        if ( *(_BYTE *)(dword_3AD2F8 + 8) )
        {
          sub_95F30(0);
          (*(void (__thiscall **)(int, int))(*(_DWORD *)dword_3AD2F8 + 4))(dword_3AD2F8, 4);
          v29 = 1;
        }
        v11 = *(_DWORD *)(mcConfig__GetPlayer_int(dword_3ACE94) + 80);
        v26 = v11;
        if ( a2 == dword_3ACE94 )
        {
          (*(void (__fastcall **)(_DWORD, _DWORD *, _DWORD))(**(_DWORD **)(v11 + 48) + 48))(
            *(_DWORD *)(v11 + 48),
            &this[40 * dword_3ACE94 + 34],
            0);
          (*(void (__thiscall **)(_DWORD, _DWORD))(**(_DWORD **)(v26 + 44) + 48))(*(_DWORD *)(v26 + 44), 0);
          if ( (unsigned __int8)sub_A3EC0(a2) )
          {
            char_const__ptr = txtStringTable__Get_char_const__ptr("hud_you_win");
            sub_B9680(8, *(_DWORD *)(char_const__ptr + 8));
            return sub_B8670(8);
          }
          else
          {
            v13 = txtStringTable__Get_char_const__ptr("hud_you_lose");
            sub_B9680(9, *(_DWORD *)(v13 + 8));
            return sub_B8670(9);
          }
        }
        else if ( !LOBYTE(this[40 * dword_3ACE94 + 35])
               || (unsigned __int8)sub_B86D0(8)
               || (unsigned __int8)sub_B86D0(9) )
        {
          result = byte_3ACE91;
          if ( byte_3ACE91 )
          {
            v14 = v27;
            result = *((_BYTE *)v27 + 142);
            if ( !result )
            {
              mcControlConfigMap__ClearAllMaps_void(v24[0]);
              v15 = sub_1AEC0(v24, "%s %s", 6);
              v16 = txtStringTable__Get_char_const__ptr("PL_Finished");
              stprintf_unsigned_wchar_t__ptr__unsigned_wchar_t_const__ptr___varargs(
                v25,
                v15,
                v14 + 53,
                *(_DWORD *)(v16 + 8));
              sub_B9680(10, v25);
              sub_B8670(10);
              result = v29;
              if ( v29 )
                return mcPlayerManager__SetInputEnable_bool_bool(1, 1);
            }
          }
        }
        else
        {
          return (*(int (__thiscall **)(_DWORD *, int))(*this + 152))(this, 1);
        }
        return result;
      }
      v17 = *(_DWORD *)(mcConfig__GetPlayer_int(a2) + 80);
      (*(void (__thiscall **)(_DWORD, _DWORD))(**(_DWORD **)(v17 + 48) + 48))(*(_DWORD *)(v17 + 48), 0);
      (*(void (__thiscall **)(_DWORD, _DWORD))(**(_DWORD **)(v17 + 44) + 48))(*(_DWORD *)(v17 + 44), 0);
      v18 = 9;
      if ( (unsigned __int8)sub_A3EC0(a2) )
      {
        v18 = 8;
        if ( dword_3ACD50 == 12 )
        {
          v18 = 19;
          v20 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("hud_lost_cops_and_won") + 8);
          sub_B9680(19, v20);
        }
        else
        {
          v21 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("hud_you_win") + 8);
          sub_B9680(8, v21);
        }
        sub_140B80(dword_3B6774);
        goto LABEL_52;
      }
      if ( *((_BYTE *)v27 + 141) )
      {
        v19 = txtStringTable__Get_char_const__ptr("arrested");
      }
      else
      {
        if ( *((float *)v27 + 37) == 0.0 )
        {
          v22 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("hud_time_up") + 8);
LABEL_50:
          sub_B9680(9, v22);
          goto LABEL_51;
        }
        if ( dword_3ACD50 == 12 )
        {
          v18 = 19;
          v23 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("hud_brought_cops_and_lost") + 8);
          sub_B9680(19, v23);
LABEL_51:
          sub_140BC0(dword_3B6774);
LABEL_52:
          sub_B8670(v18);
          return (*(int (__thiscall **)(int, int))(*(_DWORD *)dword_3AD30C + 4))(
                   dword_3AD30C,
                   (this[1122] == dword_3ACD74) + 6);
        }
        v19 = txtStringTable__Get_char_const__ptr("hud_you_lose");
      }
      v22 = *(_DWORD *)(v19 + 8);
      goto LABEL_50;
    }
  }
  return result;
}

```

### `mcRaceHookmen__PostLevelLoad_void`
- **MC2 Xbox VA:** `0x0ADDA0..0xadf0a` (368 B) | **MC3 Xbox VA:** `0x1D7AB0` (320 B, delta: `-48 B`) | **MC3 PS2 VA:** `0x3E8248`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_e4c979c9fab4b7e654ef06540d66eb59c9a46b3708a37e74b547c0f6ee1bb61d`

```cpp
int __thiscall mcRaceHookmen__PostLevelLoad_void(_DWORD *this)
{
  _DWORD *v1; // ebp
  int result; // eax
  int v3; // esi
  _DWORD *i; // edi
  int Player_int; // eax
  int v6; // ebx
  int v7; // eax
  bool v8; // cc
  int *v10; // [esp+Ch] [ebp-4h]

  v1 = this;
  sub_9F150();
  result = dword_3ACD74;
  v3 = 0;
  if ( dword_3ACD74 > 0 )
  {
    v10 = v1 + 1126;
    for ( i = v1 + 37; *((_BYTE *)i - 8); i += 40 )
    {
LABEL_23:
      result = dword_3ACD74;
      ++v3;
      ++v10;
      if ( v3 >= dword_3ACD74 )
        return result;
    }
    Player_int = mcConfig__GetPlayer_int(v3);
    v6 = sub_C2A00(Player_int);
    if ( (unsigned __int8)sub_ADD50(v3) )
    {
      if ( v6 )
        *((_BYTE *)i + 61) = 0;
      else
        *((_BYTE *)i + 61) = 1;
      *(float *)i = *(float *)(dword_3AD30C + 12);
      (*(void (__thiscall **)(_DWORD *, int))(*v1 + 48))(v1, v3);
      *((_BYTE *)i - 8) = 1;
      goto LABEL_23;
    }
    v7 = *v10;
    v8 = v6 < *v10;
    if ( v6 > *v10 )
    {
      if ( !v7 )
      {
        mcConfig__GetPlayer_int(v3);
        if ( !(unsigned __int8)sub_B86D0(5) && !(unsigned __int8)sub_B86D0(4) && !(unsigned __int8)sub_B86D0(6) )
        {
          sub_B8670(5);
          *v10 = v6;
        }
LABEL_22:
        v1 = this;
        goto LABEL_23;
      }
      v8 = v6 < v7;
    }
    if ( !v8 || v6 )
      goto LABEL_23;
    mcConfig__GetPlayer_int(v3);
    if ( !(unsigned __int8)sub_B86D0(5) && !(unsigned __int8)sub_B86D0(4) && !(unsigned __int8)sub_B86D0(6) )
    {
      sub_B8670(6);
      *v10 = 0;
    }
    goto LABEL_22;
  }
  return result;
}

```

### `mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int`
- **MC2 Xbox VA:** `0x0AE2C0..0xae4f7` (576 B) | **MC3 Xbox VA:** `0x1D75A0` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x3E7660`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_a48668c418ec5aa93dfde13f1be246a78841532b21f920fa2593e0a7cd776181`

```cpp
int __thiscall mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int(
        _DWORD *this,
        int a2,
        int a3,
        int a4)
{
  int v5; // eax
  int v6; // esi
  int result; // eax
  int v8; // esi
  int v9; // edi
  int Player_int; // eax
  int v11; // eax
  int v12; // eax
  const char *v13; // eax
  unsigned int v14; // kr00_4
  int v15; // eax
  int v16; // [esp-4h] [ebp-48h]
  char v17[12]; // [esp+0h] [ebp-44h] BYREF
  _BYTE v18[160]; // [esp+Ch] [ebp-38h] BYREF
  int v19; // [esp+ACh] [ebp+68h]
  const char *v20; // [esp+B8h] [ebp+74h]

  v19 = *(_DWORD *)(*(_DWORD *)(mcConfig__GetPlayer_int(a2) + 80) + 52);
  switch ( a4 )
  {
    case 4:
    case 2:
      sub_20DF7F(v18, *(_DWORD *)(this[a4 + 1132] + 8));
      goto LABEL_18;
    case 3:
      mcControlConfigMap__ClearAllMaps_void(v17[0]);
      v16 = this[1125];
      v5 = sub_1AEC0(v17, "%d", 3);
      stprintf_unsigned_wchar_t__ptr__unsigned_wchar_t_const__ptr___varargs(v18, v5, v16);
      goto LABEL_5;
    case 5:
      if ( dword_3AC6F0 )
      {
        mcControlConfigMap__ClearAllMaps_void(v17[0]);
        v12 = sub_1AEC0(v17, "%s %s", (const char *)6);
        v9 = *(_DWORD *)(this[1137] + 8);
        v8 = v12;
      }
      else
      {
        mcControlConfigMap__ClearAllMaps_void(v17[0]);
        v8 = sub_1AEC0(v17, "%s %s", (const char *)6);
        v9 = *(_DWORD *)(this[1137] + 8);
      }
      Player_int = mcConfig__GetPlayer_int(0);
      v11 = sub_80860(*(_DWORD *)(*(_DWORD *)(Player_int + 16) + 68));
      stprintf_unsigned_wchar_t__ptr__unsigned_wchar_t_const__ptr___varargs(v18, v8, *(_DWORD *)(v11 + 8), v9);
      v6 = 12;
      goto LABEL_6;
  }
  result = a3;
  if ( a3 )
  {
    v13 = (&(&off_34FDBC)[1182 * dword_3ACD38])[*(char *)(*(_DWORD *)(a3 + 88) + 24)];
    v20 = v13;
    if ( v13 )
    {
      v14 = strlen(v13);
      mcControlConfigMap__ClearAllMaps_void(v17[0]);
      sub_1AEC0(v17, v20, v14 + 1);
    }
    mcControlConfigMap__ClearAllMaps_void(v17[0]);
    v15 = sub_1AEC0(v17, "%s %s", (const char *)6, *(const char **)(this[a4 + 1132] + 8));
    stprintf_unsigned_wchar_t__ptr__unsigned_wchar_t_const__ptr___varargs(v18, v15);
LABEL_18:
    if ( a4 != 2 )
    {
      v6 = 11;
      goto LABEL_6;
    }
LABEL_5:
    v6 = 14 - ((this[1125] & 1) != 0);
LABEL_6:
    sub_B9680(v6, v18);
    return sub_B8670(v6);
  }
  return result;
}

```

### `mcRaceHookmen__PlayerFinishedFollow_void`
- **MC2 Xbox VA:** `0x0AE500..0xae592` (160 B) | **MC3 Xbox VA:** `0x1D7780` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x3E7C58`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_c583406bc6c66b5be0562eb76489a0bca86529b793531450d85c97aac5c0e758`

```cpp
int __thiscall mcRaceHookmen__PlayerFinishedFollow_void(int this)
{
  double v2; // st7
  int char_const__ptr; // eax
  int result; // eax

  mcMenuControllerConfig__ResetPrevAxisValues_void(3);
  sub_140E60(dword_3B6774);
  *(_BYTE *)(this + 140) = 1;
  v2 = *(float *)(dword_3AD30C + 12);
  *(_BYTE *)(this + 209) = 1;
  *(float *)(this + 148) = v2;
  sub_9DF10(0);
  mcConfig__GetPlayer_int(0);
  char_const__ptr = txtStringTable__Get_char_const__ptr("Follow Completed");
  sub_B9680(19, *(_DWORD *)(char_const__ptr + 8));
  result = sub_B8670(19);
  if ( *(_DWORD *)(dword_3AD30C + 4) != 7 )
    return (*(int (__thiscall **)(int, int))(*(_DWORD *)dword_3AD30C + 4))(dword_3AD30C, 7);
  return result;
}

```

### `mcRaceHookmen__LoadAllHookmanSubRaces_void`
- **MC2 Xbox VA:** `0x0AEA80..0xaebe7` (368 B) | **MC3 Xbox VA:** `0x1D6D70` (560 B, delta: `+192 B`) | **MC3 PS2 VA:** `0x3E8248`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_f446da4e067b47d5035f37dd8fa4847121f0abd64ec9e2b90ac86efde5702b3f`

```cpp
int __thiscall mcRaceHookmen__LoadAllHookmanSubRaces_void(_DWORD *this)
{
  int v2; // edi
  _DWORD *v3; // eax
  _DWORD *v4; // ebp
  _DWORD *v5; // ebx
  int v6; // ebx
  int v7; // eax
  int v8; // ebp
  int v9; // ebx
  int v10; // edi
  int v11; // ebx
  int v12; // edi
  _DWORD *v13; // eax
  _DWORD *v14; // ebp
  _DWORD *v15; // ebx
  _DWORD *v16; // eax
  int v17; // edi
  _DWORD *v18; // eax
  _DWORD *v19; // ebp
  _DWORD *v20; // ebx
  int v21; // eax
  int v22; // eax
  int v23; // ecx
  int result; // eax
  int v25; // [esp-8h] [ebp-18h]
  int v26; // [esp-4h] [ebp-14h]

  v2 = this[3];
  v3 = (_DWORD *)sub_1789E0(124 * v2 + 4);
  if ( v3 )
  {
    v4 = v3 + 1;
    *v3 = v2;
    v5 = v3 + 1;
    if ( v2 - 1 >= 0 )
    {
      do
      {
        sub_9E4F0(v5);
        v5 += 31;
        --v2;
      }
      while ( v2 );
    }
  }
  else
  {
    v4 = 0;
  }
  v6 = this[3];
  this[7] = v4;
  v7 = sub_1789E0(76 * v6);
  v8 = v7;
  if ( v7 )
  {
    v9 = v6 - 1;
    v10 = v7;
    if ( v9 >= 0 )
    {
      v11 = v9 + 1;
      do
      {
        sub_A1C80(v10);
        v10 += 76;
        --v11;
      }
      while ( v11 );
    }
  }
  else
  {
    v8 = 0;
  }
  v12 = this[3];
  this[354] = v8;
  v13 = (_DWORD *)sub_1789E0(4488 * v12 + 4);
  if ( v13 )
  {
    v14 = v13 + 1;
    *v13 = v12;
    v15 = v13 + 1;
    if ( v12 - 1 >= 0 )
    {
      do
      {
        sub_AF3C0(v15);
        v15 += 1122;
        --v12;
      }
      while ( v12 );
    }
    v16 = v14;
  }
  else
  {
    v16 = 0;
  }
  v17 = this[3];
  this[1128] = v16;
  v18 = (_DWORD *)sub_1789E0(4488 * v17 + 4);
  if ( v18 )
  {
    v19 = v18 + 1;
    *v18 = v17;
    v20 = v18 + 1;
    if ( v17 - 1 >= 0 )
    {
      do
      {
        sub_AF3C0(v20);
        v20 += 1122;
        --v17;
      }
      while ( v17 );
    }
  }
  else
  {
    v19 = 0;
  }
  v26 = 4 * this[3];
  this[1130] = v19;
  v21 = sub_1789E0(v26);
  v25 = 4 * this[3];
  this[1129] = v21;
  v22 = sub_1789E0(v25);
  v23 = this[3];
  this[1131] = v22;
  result = 0;
  if ( v23 > 0 )
  {
    do
    {
      *(_DWORD *)(this[1129] + 4 * result) = 0;
      *(_DWORD *)(this[1131] + 4 * result++) = 0;
    }
    while ( result < this[3] );
  }
  return result;
}

```

### `mcRaceHookmen__Update_void`
- **MC2 Xbox VA:** `0x0AEEF0..0xaf2e4` (1024 B) | **MC3 Xbox VA:** `0x1D7C00` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x3E7588`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_658d64d658a251a29314112e84c8965236e6700f6a022082ed55319315eb7c05`

```cpp
int __thiscall mcRaceHookmen__Update_void(int this)
{
  int v2; // edi
  int v3; // ebp
  _DWORD *v4; // ebx
  int v5; // edi
  int v6; // ebp
  int v7; // edi
  int v8; // ecx
  int v9; // eax
  double v10; // st7
  double v11; // st6
  bool v12; // cc
  double v13; // st7
  int v14; // eax
  int v15; // ebx
  int v16; // ebx
  int v17; // eax
  int result; // eax
  char v19; // [esp+13h] [ebp-1Dh]
  int v20; // [esp+14h] [ebp-1Ch]
  int v21; // [esp+18h] [ebp-18h]
  int v22; // [esp+1Ch] [ebp-14h]
  int v23; // [esp+20h] [ebp-10h]
  int v24; // [esp+24h] [ebp-Ch]
  int v25; // [esp+28h] [ebp-8h]
  int v26; // [esp+2Ch] [ebp-4h]

  sub_9F150();
  v2 = 0;
  v3 = 0;
  v19 = 0;
  v25 = 0;
  v21 = 0;
  v22 = 0;
  v26 = 0;
  v24 = 0;
  v4 = (_DWORD *)sub_7DC50(0);
  v23 = 0;
  if ( *(int *)(this + 12) > 0 )
  {
    v20 = 0;
    do
    {
      v5 = *(_DWORD *)(dword_381EEC + 8);
      v6 = *(_DWORD *)(v5 + v20 + 88);
      v7 = v20 + v5;
      if ( *(_DWORD *)(v6 + 8) == 2 )
      {
        if ( (*(unsigned __int8 (__thiscall **)(int))(*(_DWORD *)v6 + 40))(v6) )
        {
          v8 = v4[4];
          v9 = *(_DWORD *)(v7 + 28);
          v10 = *(float *)(v8 + 52) - *(float *)(v9 + 52);
          v11 = *(float *)(v8 + 60) - *(float *)(v9 + 60);
          if ( v11 * v11 + v10 * v10 < 784.0 )
            v19 = 1;
        }
        if ( *(_BYTE *)(v6 + 1000) )
        {
          v25 = v7;
        }
        else if ( (unsigned __int8)sub_C7910(v6) )
        {
          v21 = v7;
          if ( (unsigned __int8)aiBrainHookman__IsEngagedAndReadyForRace_void_const(v6) )
          {
            v22 = v7;
            v24 = floorf(*(float *)(v6 + 988)) + 1;
          }
        }
        else if ( *(_BYTE *)(this + 4488) && (unsigned __int8)sub_C7930(v6) )
        {
          v26 = v7;
        }
      }
      v12 = ++v23 < *(_DWORD *)(this + 12);
      v20 += 1068;
    }
    while ( v12 );
    if ( v19 )
    {
      if ( !*(_BYTE *)(this + 5) )
      {
        mcRaceHookmen__PlayerFinishedFollow_void(this);
        *(_BYTE *)(this + 5) = 1;
      }
      goto LABEL_48;
    }
    v3 = v24;
    v2 = v25;
  }
  if ( !*(_BYTE *)(this + 5) && *(int *)(dword_3AD30C + 4) < 7 )
  {
    if ( v2 )
    {
      if ( *(_BYTE *)(this + 4488) )
      {
        if ( *(float *)(this + 4492) == 0.0 )
        {
          *(_DWORD *)(this + 4492) = 1082130432;
          *(_DWORD *)(this + 4504) = 1091567616;
          mcMenuControllerConfig__ResetPrevAxisValues_void(3);
          mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v2, 1);
        }
        else
        {
          v13 = *(float *)(this + 4492) - flt_356D90;
          *(float *)(this + 4492) = v13;
          if ( v13 < 0.0 )
          {
            *(_DWORD *)(this + 4492) = 0;
            *(_DWORD *)(this + 4504) = 1056964608;
            sub_E9060(*(_DWORD *)(*(_DWORD *)(v4[4] + 72) + 464));
            sub_E9E40(*(_DWORD *)(v4[4] + 72));
            (*(void (__thiscall **)(_DWORD *))(*v4 + 24))(v4);
            sub_C79A0(*(_DWORD *)(v2 + 88));
            mcProgressManager__SelectHookmanRaceFromFollow_int_int(*(_BYTE *)(v2 + 80));
            v14 = sub_8EEB0();
            sub_8EA60(v14);
            v15 = v4[26];
            if ( v15 )
              sub_11A720(v15);
          }
        }
      }
      else
      {
        sub_E9060(*(_DWORD *)(*(_DWORD *)(v4[4] + 72) + 464));
        sub_E9E40(*(_DWORD *)(v4[4] + 72));
        v16 = v4[26];
        if ( v16 )
          sub_11A720(v16);
        mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v2, 1);
        sub_C79A0(*(_DWORD *)(v2 + 88));
      }
    }
    else
    {
      if ( v21 && !*(_BYTE *)(this + 4496) && *(_DWORD *)(*(_DWORD *)(v4[4] + 72) + 440) != 2 )
      {
        *(_BYTE *)(this + 4496) = 1;
        mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v21, 0);
        mcMenuControllerConfig__ResetPrevAxisValues_void(0);
        sub_140E10(0, *(__int16 *)(v21 + 80));
        goto LABEL_48;
      }
      if ( v22 )
      {
        v17 = *(_DWORD *)(this + 4500);
        if ( v17 != v3 )
        {
          *(_DWORD *)(this + 4500) = v3;
          if ( v17 )
          {
            mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v22, 3);
          }
          else
          {
            mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v22, 2);
            sub_140E40(dword_3B6774);
          }
          goto LABEL_48;
        }
      }
      else if ( *(_DWORD *)(this + 4500) )
      {
        mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, v21, 4);
        sub_140E50(dword_3B6774);
        goto LABEL_48;
      }
      if ( v26 && *(float *)(dword_3AD30C + 12) > 0.0 )
      {
        mcMenuControllerConfig__ResetPrevAxisValues_void(1);
        if ( *(float *)(this + 4504) >= 0.0 )
        {
          *(float *)(this + 4504) = *(float *)(this + 4504) - flt_356D90;
        }
        else
        {
          mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int((_DWORD *)this, 0, 0, 5);
          *(_DWORD *)(this + 4504) = 1077936128;
        }
      }
    }
  }
LABEL_48:
  if ( !v21 )
    *(_BYTE *)(this + 4496) = 0;
  result = v22;
  if ( !v22 )
    *(_DWORD *)(this + 4500) = 0;
  return result;
}

```

### `mcRaceHookmen__Load_char_const__ptr__char_const__ptr`
- **MC2 Xbox VA:** `0x0AF2F0..0xaf392` (176 B) | **MC3 Xbox VA:** `0x1D6D70` (560 B, delta: `+384 B`) | **MC3 PS2 VA:** `0x3E8710`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_1eda302f4303ebd51bb74f11554760d96bf28d6ac42642536550194537907626`

```cpp
int __thiscall mcRaceHookmen__Load_char_const__ptr__char_const__ptr(int this, int a2)
{
  char **v3; // edi
  _DWORD *v4; // ebx
  int v5; // eax

  sub_A1CA0(1);
  *(_DWORD *)this = &off_32E380;
  *(_DWORD *)(this + 12) = a2;
  *(_BYTE *)(this + 4488) = 1;
  *(_BYTE *)(this + 4489) = 1;
  mcRaceHookmen__LoadAllHookmanSubRaces_void((_DWORD *)this);
  v3 = off_32E314;
  v4 = (_DWORD *)(this + 4528);
  do
  {
    if ( *v3 )
      *v4 = txtStringTable__Get_char_const__ptr(*v3);
    else
      *v4 = 0;
    ++v3;
    ++v4;
  }
  while ( (int)v3 < (int)"hud_flash_lights" );
  switch ( dword_3ACD38 )
  {
    case 0:
      v5 = StringDuplicate_char_const__ptr("moses");
      goto LABEL_12;
    case 1:
      v5 = StringDuplicate_char_const__ptr("gina");
      goto LABEL_12;
    case 2:
      v5 = StringDuplicate_char_const__ptr("gina_tokyo");
LABEL_12:
      *(_DWORD *)(this + 1528) = v5;
      break;
  }
  return this;
}

```

### `mcRaceAmbient__LoadProperties_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x0B0170..0xb020b` (160 B) | **MC3 Xbox VA:** `0x1D5B70` (148 B, delta: `-12 B`) | **MC3 PS2 VA:** `0x3D0708`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_bf89b141cce871889269ba492ad9ec01eeb50cc93525787bb09deb0e7f3d92f0`

```cpp
int __thiscall mcRaceAmbient__LoadProperties_datAsciiTokenizer__ref(int this, int a2)
{
  int result; // eax

  datBaseTokenizer__MatchIToken_char_const__ptr("Properties");
  (*(void (__thiscall **)(int, int, int))(*(_DWORD *)a2 + 4))(a2, this + 28, 100);
  *(_BYTE *)(this + 128) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  *(_BYTE *)(this + 130) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  *(_BYTE *)(this + 129) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  *(float *)(this + 136) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
  *(_BYTE *)(this + 131) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  result = datBaseTokenizer__CheckIToken_char_const__ptr__bool("MotionPathType", 1);
  if ( (_BYTE)result )
  {
    result = mcRaceAmbient__FindMotionPathType_datAsciiTokenizer__ref(a2);
    *(_DWORD *)(this + 176) = result;
  }
  return result;
}

```

### `mcHeliRace__LoadProperties_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x0C5740..0xc57c3` (144 B) | **MC3 Xbox VA:** `0x1E6C20` (129 B, delta: `-15 B`) | **MC3 PS2 VA:** `0x3FE848`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_0b9a55698573fee6e8f23942dd6149e90885402bcfbb63837568c42a6ba2d7ff`

```cpp
int __thiscall mcHeliRace__LoadProperties_datAsciiTokenizer__ref(int this, int a2)
{
  int result; // eax

  datBaseTokenizer__MatchIToken_char_const__ptr("Properties");
  *(_DWORD *)(this + 176) = mcRaceAmbient__FindMotionPathType_datAsciiTokenizer__ref(a2);
  *(_BYTE *)(this + 130) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  *(_BYTE *)(this + 129) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  *(float *)(this + 136) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
  *(_BYTE *)(this + 131) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2) > 0;
  result = datBaseTokenizer__CheckIToken_char_const__ptr__bool("HeliSearching", 1);
  *(_BYTE *)(this + 132) = (_BYTE)result != 0;
  return result;
}

```

### `aiBrainHookman__PreUpdate_void`
- **MC2 Xbox VA:** `0x0C7370..0xc73fe` (142 B) | **MC3 Xbox VA:** `0x1EB540` (1232 B, delta: `+1090 B`) | **MC3 PS2 VA:** `0x3FDE28`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_feb074662399ba7d199a9ee7c630ba4b8789e68a6ce7818611ba7ff1793f029b`

```cpp
int __cdecl aiBrainHookman__PreUpdate_void(int a1, int a2, int a3)
{
  int v3; // ecx
  int v4; // esi
  int v5; // eax
  double v6; // st7
  int v7; // edi
  int v8; // eax
  int v9; // eax

  v4 = v3;
  v5 = sub_CA930();
  sub_D2440(v5);
  v6 = *(float *)(v4 + 1052) - flt_356D90;
  *(float *)(v4 + 1052) = v6;
  if ( v6 < 0.0 )
    *(_DWORD *)(v4 + 1052) = 0;
  v7 = 0;
  if ( dword_381F4C > 0 )
  {
    while ( 1 )
    {
      v8 = sub_CA8E0(dword_381F00[v7]);
      if ( (unsigned __int8)sub_D2400(v8) )
        break;
      if ( ++v7 >= dword_381F4C )
        goto LABEL_8;
    }
    *(_DWORD *)(v4 + 1052) = 1084227584;
  }
LABEL_8:
  v9 = sub_CA940(v4);
  sub_C7310(v4, v9);
  return aiBrainHookman__Update_void(a1, a2, a3);
}

```

### `aiBrainHookman__Update_void`
- **MC2 Xbox VA:** `0x0C73FE..0xc7798` (930 B) | **MC3 Xbox VA:** `0x1EBA20` (1056 B, delta: `+126 B`) | **MC3 PS2 VA:** `0x3FDDC8`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_85efc78bb468edfaf389e5e1761d443a004812a8bcb8190410ba23ac786d9cc4`

```cpp
// positive sp value has been detected, the output may be wrong!
void __usercall aiBrainHookman__Update_void(char a1@<al>, int a2@<edx>, int a3@<esi>)
{
  int v3; // eax
  float *v4; // edi
  float *v5; // eax
  double v6; // st6
  double v7; // st4
  long double v8; // st5
  double v9; // st7
  int v10; // ebx
  int Player_int; // ebp
  float *v12; // edi
  float *v13; // eax
  double v14; // st7
  double v15; // st6
  int v16; // edi
  int v17; // eax
  int v18; // ecx
  int v19; // eax
  int v20; // ecx
  int v21; // [esp-18h] [ebp-18h]
  float v22; // [esp-4h] [ebp-4h]
  int i; // [esp-4h] [ebp-4h]

  *(_BYTE *)(*(_DWORD *)(a2 + 76) + 9820) = a1;
  if ( *(_DWORD *)(a3 + 992) && (v3 = *(_DWORD *)(a3 + 996)) != 0 )
  {
    if ( v3 == 1 && (*(_BYTE *)(a3 + 984) || *(_BYTE *)(*(_DWORD *)(a3 + 908) + 8)) )
    {
      sub_D2C50(*(_DWORD *)(a3 + 1008));
      sub_CBE00(1, 0);
      *(_BYTE *)(((int (__thiscall *)(int))sub_CA950)(a3) + 272) = 1;
      ((void (__thiscall *)(_DWORD))sub_C51F0)(*(_DWORD *)(a3 + 1008));
      (*(void (__thiscall **)(_DWORD))(**(_DWORD **)(a3 + 908) + 4))(*(_DWORD *)(a3 + 908));
      *(_DWORD *)(a3 + 996) = 2;
    }
    if ( *(_DWORD *)(a3 + 996) == 2 && *(_BYTE *)(*(_DWORD *)(a3 + 908) + 8) )
      *(_DWORD *)(a3 + 996) = 3;
    v4 = (float *)(((int (__thiscall *)(_DWORD))sub_7F960)(*(_DWORD *)(a3 + 992)) + 36);
    v5 = (float *)sub_CA8E0(a3);
    v6 = v5[2] - v4[2];
    v7 = *v5 - *v4;
    v8 = sqrt(v6 * v6 + v7 * v7);
    v22 = v8;
    if ( v8 * v22 <= *(float *)(a3 + 1012) )
    {
      *(_DWORD *)(a3 + 988) = *(_DWORD *)(a3 + 1016);
    }
    else
    {
      v9 = *(float *)(a3 + 988) - flt_356D90;
      *(float *)(a3 + 988) = v9;
      if ( v9 < 0.0 )
      {
        *(_BYTE *)(a3 + 1000) = 1;
        if ( !byte_38292C )
        {
          ((void (__thiscall *)(int))sub_140BA0)(dword_3B6774);
          byte_38292C = 1;
          ((void (__thiscall *)(int))sub_14F5B0)(dword_3AD300);
          ((void (__thiscall *)(_DWORD))sub_EB0D0)(*(_DWORD *)(*(_DWORD *)(*(_DWORD *)(a3 + 992) + 16) + 72));
          *(float *)(a3 + 32) = v22;
          return;
        }
      }
    }
    *(float *)(a3 + 32) = v22;
  }
  else if ( !*(_DWORD *)(a3 + 996) )
  {
    v10 = 0;
    if ( dword_3ACD74 > 0 )
    {
      for ( i = 8; ; i += 4 )
      {
        if ( *(_DWORD *)(i + dword_37FFE4) )
        {
          Player_int = mcConfig__GetPlayer_int(v10);
          v12 = (float *)(((int (__thiscall *)(int))sub_7F960)(Player_int) + 36);
          v13 = (float *)sub_CA8E0(a3);
          v14 = *v13 - *v12;
          v15 = v13[2] - v12[2];
          if ( flt_34E28C * flt_34E28C > v15 * v15 + v14 * v14 )
          {
            v16 = sub_CA8E0(a3);
            if ( fabs(*(float *)(v16 + 4) - *(float *)(((int (__thiscall *)(int))sub_7F960)(Player_int) + 40)) < flt_34E290
              && *(_BYTE *)(*(_DWORD *)(*(_DWORD *)(*(_DWORD *)(Player_int + 16) + 76) + 9688) + 292)
              && byte_38292C )
            {
              break;
            }
          }
        }
        if ( ++v10 >= dword_3ACD74 )
          return;
      }
      mcProgressManager__SelectHookmanRaceFromFollow_int_int(*(_BYTE *)(*(_DWORD *)(a3 + 12) + 80));
      ((void (__thiscall *)(_DWORD))sub_EB0D0)(*(_DWORD *)(*(_DWORD *)(Player_int + 16) + 72));
      byte_38292C = 0;
      if ( *(_DWORD *)(a3 + 1008) )
      {
        if ( *(float *)(a3 + 1052) == 0.0 )
        {
          v17 = mcConfig__GetPlayer_int(v10);
          v18 = *(_DWORD *)(a3 + 1008);
          *(_DWORD *)(a3 + 992) = v17;
          *(_DWORD *)(a3 + 16) = v18;
          sub_C51F0();
          if ( *(_DWORD *)(a3 + 1004) )
          {
            v21 = ((int (__thiscall *)(_DWORD))sub_C4F60)(*(_DWORD *)(a3 + 1008));
            v19 = ((int (__thiscall *)(_DWORD))sub_C4F40)(*(_DWORD *)(a3 + 1008));
            sub_D2530(v19, v21);
            sub_CBE00(5, 0);
            *(_BYTE *)(((int (__thiscall *)(int))sub_CA950)(a3) + 272) = 1;
            v20 = *(_DWORD *)(a3 + 1016);
            *(_DWORD *)(a3 + 996) = 1;
          }
          else
          {
            sub_D2C50(*(_DWORD *)(a3 + 1008));
            sub_CBE00(1, 0);
            *(_BYTE *)(((int (__thiscall *)(int))sub_CA950)(a3) + 272) = 1;
            ((void (__thiscall *)(_DWORD))sub_C51F0)(*(_DWORD *)(a3 + 1008));
            (*(void (__thiscall **)(_DWORD))(**(_DWORD **)(a3 + 908) + 4))(*(_DWORD *)(a3 + 908));
            v20 = *(_DWORD *)(a3 + 1016);
            *(_DWORD *)(a3 + 996) = 2;
          }
          *(_DWORD *)(a3 + 988) = v20;
        }
      }
      else
      {
        *(_DWORD *)(a3 + 996) = 3;
      }
    }
  }
}

```

### `aiBrainHookman__RestartCruise_void`
- **MC2 Xbox VA:** `0x0C77A0..0xc77ad` (304 B) | **MC3 Xbox VA:** `0x1EC140` (272 B, delta: `-32 B`) | **MC3 PS2 VA:** `0x3FE580`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_b9efba93e8b6d4ae849385c68318605a1f6122e2432d2847114039faf76804c4`

```cpp
int __thiscall aiBrainHookman__RestartCruise_void(void *this)
{
  int v1; // eax

  v1 = sub_CA940(this);
  return (*(int (__thiscall **)(int))(*(_DWORD *)(v1 + 64) + 4))(v1 + 64);
}

```

### `aiBrainHookman__IsEngagedAndReadyForRace_void_const`
- **MC2 Xbox VA:** `0x0C7940..0xc7962` (48 B) | **MC3 Xbox VA:** `0x1EC250` (464 B, delta: `+416 B`) | **MC3 PS2 VA:** `0x3FE810`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_6cc1fb9b4c4bf8c6fd6fb89cde14c9ee1dfff806fd4ecc7765db1db96006ede4`

```cpp
bool __thiscall aiBrainHookman__IsEngagedAndReadyForRace_void_const(void *this)
{
  int v1; // ecx

  return (unsigned __int8)sub_C7910(this) && *(float *)(v1 + 988) < (double)*(float *)(v1 + 1016);
}

```

### `mcTrainManager__LoadCityTrains_char_const__ptr`
- **MC2 Xbox VA:** `0x100530..0x10063b` (272 B) | **MC3 Xbox VA:** `0x07FC00` (252 B, delta: `-20 B`) | **MC3 PS2 VA:** `0x22F070`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_2ddeeb321afd505c16bc3e0e3779af9b221a944fd51ea30c55a65eaaafa921de`

```cpp
int __thiscall mcTrainManager__LoadCityTrains_char_const__ptr(unsigned __int16 *this, int a2)
{
  int result; // eax
  int Int_void; // eax
  _DWORD *v5; // edi
  int v6; // ebx
  int v7; // esi
  int v8; // [esp+10h] [ebp-1A8h]
  _DWORD v9[40]; // [esp+18h] [ebp-1A0h] BYREF
  char v10[254]; // [esp+B8h] [ebp-100h] BYREF
  __int16 v11; // [esp+1B6h] [ebp-2h]

  sub_100240();
  sub_10F490(a2);
  strcpy(v10, "tune/city");
  memset(&v10[10], 0, 0xF4u);
  v11 = 0;
  v9[0] = &off_33ECE8;
  v9[39] = 0;
  result = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(v10, a2, "Train", 0, 1);
  v8 = result;
  if ( result )
  {
    datBaseTokenizer__Init_char_const__ptr__Stream__ptr(a2, result);
    datBaseTokenizer__MatchIToken_char_const__ptr("NumTrains");
    Int_void = datAsciiTokenizer__GetInt_void(v9);
    v5 = this + 2;
    v6 = Int_void;
    if ( Int_void > this[4] )
      sub_1003E0(Int_void);
    this[4] = v6;
    if ( v6 > 0 )
    {
      v7 = 0;
      do
      {
        sub_10EFF0(v7 + *v5, v9);
        v7 += 32;
        --v6;
      }
      while ( v6 );
    }
    return Stream__Close_void(v8);
  }
  return result;
}

```

### `mcRaceConfig__SetCity_char_const__ptr`
- **MC2 Xbox VA:** `0x14E790..0x14e7d6` (80 B) | **MC3 Xbox VA:** `0x26B050` (80 B, delta: `+0 B`) | **MC3 PS2 VA:** `0x4BE708`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_49f050b6dfa6ab7c397691dc438c8ba6458a69927f681dc9b357eecff2fd8ad9`

```cpp
int __thiscall mcRaceConfig__SetCity_char_const__ptr(_DWORD *this, int a2)
{
  int v3; // esi
  int result; // eax

  v3 = 0;
  while ( 1 )
  {
    result = strcasecmp(off_34F2E4[v3], a2);
    if ( !result )
      break;
    if ( ++v3 >= 4 )
      strcmp("mcData: Unknown cityname!");
  }
  *this = v3;
  return result;
}

```

### `mcRaceConfig__LoadInfo_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x14EB40..0x14ec7e` (320 B) | **MC3 Xbox VA:** `0x26B770` (358 B, delta: `+38 B`) | **MC3 PS2 VA:** `0x4BE1C8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_abb025b2d30de71dbbf32b97796560946a99eb08314295765261c2f8f5210d8f`

```cpp
char __thiscall mcRaceConfig__LoadInfo_datAsciiTokenizer__ref(int this, int a2)
{
  int v4; // eax
  _BYTE v6[128]; // [esp+20h] [ebp-80h] BYREF

  datBaseTokenizer__MatchIToken_char_const__ptr("city");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v6, 128);
  mcRaceConfig__SetCity_char_const__ptr((_DWORD *)this, (int)v6);
  datBaseTokenizer__MatchIToken_char_const__ptr("time");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v6, 128);
  mcRaceConfig__SetTOD_char_const__ptr(v6);
  datBaseTokenizer__MatchIToken_char_const__ptr("weather");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v6, 128);
  mcRaceConfig__SetWeather_char_const__ptr(v6);
  datBaseTokenizer__MatchIToken_char_const__ptr("racetype");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v6, 128);
  mcRaceConfig__SetRaceType_char_const__ptr(v6);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("AmbientDensity", 1) )
    (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 20))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("PedDensity", 1) )
    (*(void (__thiscall **)(int))(*(_DWORD *)a2 + 20))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("ForcedCar", 1) )
    (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a2 + 4))(a2, v6, 128);
  v4 = *(_DWORD *)(this + 24);
  *(_BYTE *)(this + 56) = -1;
  *(_BYTE *)(this + 57) = 0;
  if ( v4 == 10 || v4 == 11 )
    *(_DWORD *)(this + 28) = 1;
  *(_DWORD *)(this + 20) = 1;
  return 1;
}

```

### `mcRaceConfig__LoadRaceInfo_void`
- **MC2 Xbox VA:** `0x14ED80..0x14ee45` (208 B) | **MC3 Xbox VA:** `0x26BAB0` (205 B, delta: `-3 B`) | **MC3 PS2 VA:** `0x4BE0D0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_66e1d509c75b5e47e261b151bcf72c66ea1c55d8dc232321bddab2849e382f67`

```cpp
char __thiscall mcRaceConfig__LoadRaceInfo_void(const char *this)
{
  char *v2; // edi
  int Data_datBinTokenizer__ref__phBound__FileVersion; // eax
  int v4; // esi
  char Info_datAsciiTokenizer__ref; // bl
  _DWORD v7[40]; // [esp+10h] [ebp-1A0h] BYREF
  _BYTE v8[256]; // [esp+B0h] [ebp-100h] BYREF

  v2 = (char *)(this + 88);
  if ( this == (const char *)-88 )
    return 0;
  if ( !strlen(this + 88) )
    return 0;
  strlen(v8, 256, "tune/race/%s", off_34F2E4[*(_DWORD *)this]);
  Data_datBinTokenizer__ref__phBound__FileVersion = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
                                                      v8,
                                                      v2,
                                                      "rinf",
                                                      1,
                                                      1);
  v4 = Data_datBinTokenizer__ref__phBound__FileVersion;
  if ( !Data_datBinTokenizer__ref__phBound__FileVersion )
    return 0;
  v7[0] = &off_33ECE8;
  v7[39] = 0;
  datBaseTokenizer__Init_char_const__ptr__Stream__ptr(v2, Data_datBinTokenizer__ref__phBound__FileVersion);
  Info_datAsciiTokenizer__ref = mcRaceConfig__LoadInfo_datAsciiTokenizer__ref((int)this, (int)v7);
  Stream__Close_void(v4);
  return Info_datAsciiTokenizer__ref;
}

```

### `mcProgressManager__IsRaceBeaten_int_int_const`
- **MC2 Xbox VA:** `0x14EFF0..0x14f041` (96 B) | **MC3 Xbox VA:** `0x27D350` (240 B, delta: `+144 B`) | **MC3 PS2 VA:** `0x4C8990`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_fd8a9a26d07c09e19b7558c10e0ed868f8391341e300038261306ba79595000a`

```cpp
bool __thiscall mcProgressManager__IsRaceBeaten_int_int_const(_DWORD *this, int a2, int a3)
{
  if ( this[1] == 1 )
    return 0;
  if ( a2 < 3 )
    return (sub_20F2F0(a3, 0) & *(_QWORD *)&this[2 * a2 + 12]) != 0;
  return 0;
}

```

### `mcProgressManager__SelectHookmanRaceFromFollow_int_int`
- **MC2 Xbox VA:** `0x14F560..0x14f5a5` (80 B) | **MC3 Xbox VA:** `0x276FC0` (160 B, delta: `+80 B`) | **MC3 PS2 VA:** `0x4C0060`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_5e2007c78e07f28e71a344ab0104ba378604b46d15b735b0469e4067c1a08828`

```cpp
int __thiscall mcProgressManager__SelectHookmanRaceFromFollow_int_int(int this, unsigned __int8 a2)
{
  int result; // eax
  unsigned __int8 v3; // dl
  int v4; // esi

  result = 1;
  if ( *(_DWORD *)(this + 4) != 1 )
  {
    v3 = byte_3AD074[4 * a2];
    *(_BYTE *)(this + 80) = 1;
    v4 = *(_DWORD *)(this + 24);
    *(_BYTE *)(this + 39) = v3;
    result = dword_34FE30[1182 * v4 + 33 * v3 + *(unsigned __int8 *)(v3 + this + 28)];
    *(_DWORD *)(this + 12) = result;
  }
  return result;
}

```

### `mcProgressManager__UpdateHookmanRacesCompleted_int_int`
- **MC2 Xbox VA:** `0x14F5F0..0x14f655` (112 B) | **MC3 Xbox VA:** `0x277350` (240 B, delta: `+128 B`) | **MC3 PS2 VA:** `0x4C02C0`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_84711cb0357b0c217dfa1ec5ce4545bfe97461ede4c75229d3c82833c6ee867d`

```cpp
int __thiscall mcProgressManager__UpdateHookmanRacesCompleted_int_int(void *this)
{
  int v2; // edi
  int *v3; // ebp
  int v4; // esi

  v2 = 0;
  v3 = dword_34FDB8;
  while ( 1 )
  {
    v4 = 0;
    if ( *v3 > 0 )
      break;
LABEL_6:
    v3 += 1182;
    ++v2;
    if ( (int)v3 >= (int)dword_353520 )
      return 3;
  }
  while ( mcProgressManager__GetHookmanState_int_int_const((int)this, v2, v4, 1)
       || (unsigned __int8)mcUnlocking__PackItemKey_int_int(v2, v4) != 1 )
  {
    if ( ++v4 >= *v3 )
      goto LABEL_6;
  }
  return v2;
}

```

### `mcProgressManager__MarkRaceAsBeaten_int_int`
- **MC2 Xbox VA:** `0x14F770..0x14f82c` (192 B) | **MC3 Xbox VA:** `0x277CA0` (384 B, delta: `+192 B`) | **MC3 PS2 VA:** `0x4C0708`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_8a6a4c51a7a296c526aa8ce59affccfa7a16c8cbfc590652dc64de9e28c457be`

```cpp
int __thiscall mcProgressManager__MarkRaceAsBeaten_int_int(_BYTE *this, int a2, int a3)
{
  int v3; // ebx
  int v4; // edi
  int v6; // ebp
  __int64 v7; // rax
  int v8; // ebp
  int result; // eax
  __int64 v10; // rax
  int v11; // ecx
  int v12; // [esp+10h] [ebp-8h]
  int v13; // [esp+14h] [ebp-4h]

  v3 = a3;
  v4 = a2;
  v6 = *(_DWORD *)&this[8 * a2 + 48];
  v12 = v6;
  v13 = *(_DWORD *)&this[8 * a2 + 52];
  if ( !(unsigned __int8)sub_14F080(a2, a3) )
    strcmp(
      "mcProgressManager::MarkRaceAsBeaten was called for a race that is considered unbeatable: cityidx: %d, raxeidx: %d",
      v4,
      v3);
  v7 = sub_20F2F0(v3, 0);
  LODWORD(v7) = v6 | v7;
  v8 = *(_DWORD *)&this[8 * v4 + 52];
  *(_DWORD *)&this[8 * v4 + 48] = v7;
  *(_DWORD *)&this[8 * v4 + 52] = v8 | HIDWORD(v7);
  result = sub_150770(v4, v3, &a2);
  if ( (_BYTE)result )
  {
    v10 = sub_20F2F0(a2, 0);
    v11 = v10 | *(_DWORD *)&this[8 * v4 + 48];
    result = HIDWORD(v10) | *(_DWORD *)&this[8 * v4 + 52];
    *(_DWORD *)&this[8 * v4 + 48] = v11;
    *(_DWORD *)&this[8 * v4 + 52] = result;
  }
  if ( *(_DWORD *)&this[8 * v4 + 48] != v12 || *(_DWORD *)&this[8 * v4 + 52] != v13 )
    this[80] = 1;
  return result;
}

```

### `mcProgressManager__CheckAndRequestPostRaceMovie_int_int`
- **MC2 Xbox VA:** `0x14F8C0..0x14f9e7` (304 B) | **MC3 Xbox VA:** `0x277760` (464 B, delta: `+160 B`) | **MC3 PS2 VA:** `0x4C00C8`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_d452b5ccc2555c63724a55ab414e16f3b365d3a0a6b19e148dc86a20f1add98d`

```cpp
char __thiscall mcProgressManager__CheckAndRequestPostRaceMovie_int_int(int this)
{
  int v2; // edi
  int v3; // ebx
  int v4; // edi
  int v5; // eax
  char v7; // [esp+Bh] [ebp-9h]
  int *v8; // [esp+Ch] [ebp-8h]
  int v9; // [esp+10h] [ebp-4h]

  v2 = *(_DWORD *)(this + 12);
  v9 = v2;
  if ( !(unsigned __int8)mcProgressManager__AreMoviesDisabled_void() && v2 != -1 && *(_DWORD *)(this + 4) != 6 )
  {
    if ( *(_BYTE *)(this + 39) == 0xFF )
    {
      v3 = *(_DWORD *)(this + 24);
      v4 = 0;
      v7 = 1;
      if ( dword_34FDB8[1182 * v3] > 0 )
      {
        v8 = &dword_34FDF0[1182 * v3];
        do
        {
          if ( !mcProgressManager__GetHookmanState_int_int_const(this, v3, v4, 1)
            && (unsigned __int8)mcUnlocking__PackItemKey_int_int(v3, v4) == 1
            && *v8 < 0 )
          {
            v7 = 0;
          }
          ++v4;
          v8 += 33;
        }
        while ( v4 < dword_34FDB8[1182 * v3] );
      }
      if ( !v7 )
      {
        v5 = dword_350680[1182 * *(_DWORD *)(this + 24) + v9];
        if ( v5 )
          goto LABEL_16;
      }
      v2 = v9;
    }
    v5 = dword_350590[1182 * *(_DWORD *)(this + 24) + v2];
    if ( v5 )
    {
LABEL_16:
      sub_14E9F0(v5);
      sub_14E9D0(&byte_31FF74);
      sub_14E980(&byte_31FF74);
      *(_DWORD *)(this + 4) = 6;
      return 1;
    }
  }
  return 0;
}

```

### `mcProgressManager__CheckAndRequestPreRaceMovie_int_int`
- **MC2 Xbox VA:** `0x14F9F0..0x14fa7d` (144 B) | **MC3 Xbox VA:** `0x2774B0` (128 B, delta: `-16 B`) | **MC3 PS2 VA:** `0x4C0C78`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_cc8bf1714ffde1fa3f196c38a2a912c59c2a1c72a2f84c5cc22804584c7eaf21`

```cpp
char __thiscall mcProgressManager__CheckAndRequestPreRaceMovie_int_int(_DWORD *this)
{
  int v2; // ebp
  int v3; // ecx
  int v4; // ebx
  int v5; // esi
  int v7; // [esp+10h] [ebp-4h]

  v2 = this[6];
  if ( !(unsigned __int8)mcProgressManager__AreMoviesDisabled_void() )
  {
    v3 = dword_35049C[1182 * v2];
    v7 = v3;
    if ( v3 )
    {
      v4 = dword_34FDB8[1182 * v2];
      v5 = 0;
      if ( v4 <= 0 )
      {
LABEL_7:
        sub_14E9F0(v3);
        sub_14E9D0(&byte_31FF74);
        sub_14E980(&byte_31FF74);
        this[1] = 7;
        return 1;
      }
      while ( !mcProgressManager__GetHookmanState_int_int_const((int)this, v2, v5, 1) )
      {
        if ( ++v5 >= v4 )
        {
          v3 = v7;
          goto LABEL_7;
        }
      }
    }
  }
  return 0;
}

```

### `mcProgressManager__SetupNextCareerRace_void`
- **MC2 Xbox VA:** `0x14FAF0..0x14fc21` (352 B) | **MC3 Xbox VA:** `0x278270` (272 B, delta: `-80 B`) | **MC3 PS2 VA:** `0x4BFBD8`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_d98b1da6cbb5d40e88f398f337236974881f272981ca47e2e4f68500ca4970ee`

```cpp
char __thiscall mcProgressManager__SetupNextCareerRace_void(int this)
{
  int v2; // eax
  unsigned __int8 v3; // al
  int v4; // eax
  int v5; // ebp
  int v6; // edi
  char v7; // bl
  int v9; // [esp+10h] [ebp-4h]

  v2 = *(_DWORD *)(this + 4);
  if ( v2 != 1 )
  {
    *(_BYTE *)(this + 16) = 0;
    switch ( v2 )
    {
      case 0:
        v3 = *(_BYTE *)(this + 39);
        if ( v3 != 0xFF )
        {
          if ( *(_BYTE *)(v3 + this + 28) )
            goto LABEL_7;
          v4 = dword_34FE30[1182 * *(_DWORD *)(this + 24) + 33 * v3];
          if ( v4 >= 0 && mcProgressManager__IsRaceBeaten_int_int_const((_DWORD *)this, *(_DWORD *)(this + 24), v4) )
            goto LABEL_7;
        }
        v5 = *(_DWORD *)(this + 24);
        v6 = 0;
        v7 = 1;
        if ( dword_34FDB8[1182 * v5] > 0 )
        {
          v9 = dword_34FDB8[1182 * v5];
          do
          {
            if ( *(_BYTE *)(this + v6 + 28) || mcProgressManager__GetHookmanState_int_int_const(this, v5, v6, 1) )
              v7 = 0;
            ++v6;
          }
          while ( v6 < v9 );
          if ( !v7 )
            goto LABEL_17;
        }
        LOBYTE(v2) = mcProgressManager__CheckAndRequestPreRaceMovie_int_int((_DWORD *)this);
        if ( !(_BYTE)v2 )
LABEL_17:
          LOBYTE(v2) = mcProgressManager__SetupCareerCruise_int(this, *(_DWORD *)(this + 24));
        return v2;
      case 3:
      case 7:
        goto LABEL_17;
      case 4:
LABEL_7:
        LOBYTE(v2) = mcProgressManager__CheckAndRequestPreCityMovie_int(this);
        if ( !(_BYTE)v2 )
          goto LABEL_8;
        return v2;
      case 5:
LABEL_8:
        LOBYTE(v2) = sub_14F260(
                       *(_DWORD *)(this + 24),
                       *(unsigned __int8 *)(this + 39),
                       *(unsigned __int8 *)(*(unsigned __int8 *)(this + 39) + this + 28));
        break;
      case 6:
        LOBYTE(v2) = mcProgressManager__AdvanceHookmanProgress_void(this);
        break;
      case 9:
        *(_DWORD *)(this + 4) = 8;
        break;
      default:
        strcmp("mcProgressManager::SetupNextCareerRace(): Not a valid career game state for this function: %d", v2);
    }
  }
  return v2;
}

```

### `mcProgressManager__ReportRaceResult_int`
- **MC2 Xbox VA:** `0x14FCC0..0x14fdd8` (304 B) | **MC3 Xbox VA:** `0x277EE0` (512 B, delta: `+208 B`) | **MC3 PS2 VA:** `0x4BFDB0`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_fd372231738ffb93075090cc5e41c8b5c76a7d618359334ee5423416fffe08f8`

```cpp
char __thiscall mcProgressManager__ReportRaceResult_int(int this, int a2)
{
  int v3; // eax
  int v4; // edi
  int v5; // ebp
  _BYTE *v6; // ecx
  int v7; // ecx
  int updated; // eax
  char v9; // al

  v3 = *(_DWORD *)(this + 4);
  if ( v3 != 1 )
  {
    if ( a2 == 3 )
    {
      if ( v3 == 3 )
      {
        *(_BYTE *)(this + 39) = -1;
        *(_BYTE *)(this + 80) = 1;
      }
      *(_DWORD *)(this + 4) = 0;
    }
    else
    {
      if ( !a2 )
      {
        if ( v3 )
        {
          v4 = *(_DWORD *)(this + 12);
          if ( v4 != -1 && dword_3ACD74 == 1 )
          {
            v5 = dword_3ACD38;
            if ( dword_3ACD38 < 3 )
            {
              if ( (unsigned __int8)sub_14F080(dword_3ACD38, *(_DWORD *)(this + 12)) )
                mcProgressManager__MarkRaceAsBeaten_int_int(v6, v5, v4);
            }
          }
        }
      }
      v3 = *(_DWORD *)(this + 4);
      switch ( v3 )
      {
        case 0:
        case 2:
          return v3;
        case 3:
          v7 = this;
          if ( !a2 )
            goto LABEL_15;
          goto LABEL_19;
        case 4:
          if ( a2 )
          {
            LOBYTE(v3) = a2 - 2;
            if ( a2 == 2 )
            {
              *(_DWORD *)(this + 4) = 3;
              *(_BYTE *)(this + 39) = -1;
              *(_BYTE *)(this + 80) = 1;
              v7 = this;
LABEL_19:
              LOBYTE(v3) = mcProgressManager__SetupNextCareerRace_void(v7);
            }
          }
          else
          {
            mcProgressManager__MarkHookmanBeaten_int_int(this);
            updated = mcProgressManager__UpdateHookmanRacesCompleted_int_int((void *)this);
            *(_DWORD *)(this + 44) = updated;
            if ( updated == 3 )
              *(_DWORD *)(this + 44) = 0;
            if ( *(_DWORD *)(this + 44) != *(_DWORD *)(this + 24) )
              *(_BYTE *)(this + 80) = 1;
            v9 = mcProgressManager__CheckAndRequestPostRaceMovie_int_int(this);
            v7 = this;
            if ( v9 )
            {
              v3 = mcProgressManager__UpdateHookmanRacesCompleted_int_int((void *)this);
              if ( v3 == 3 )
                LOBYTE(v3) = sub_14EFB0(1);
            }
            else
            {
LABEL_15:
              LOBYTE(v3) = mcProgressManager__AdvanceHookmanProgress_void(v7);
            }
          }
          break;
        default:
          strcmp(
            "mcProgressManager::ReportRaceResult: the gamestate (%d) is not valid for calling this function",
            *(_DWORD *)(this + 4));
      }
    }
  }
  return v3;
}

```

### `mc__mcCityData__LookupHookmanRace_char_const__ptr__int`
- **MC2 Xbox VA:** `0x14FF10..0x14ff85` (128 B) | **MC3 Xbox VA:** `0x26DA10` (96 B, delta: `-32 B`) | **MC3 PS2 VA:** `0x4B7B20`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_b754e9dc881562a28666e655bea404b0c4b82cf15bce5b536ea9fb3db7e408a9`

```cpp
int __thiscall mc__mcCityData__LookupHookmanRace_char_const__ptr__int(_DWORD *this, int a2, const char *a3)
{
  int *v4; // edi
  int v5; // esi
  _DWORD *v6; // ebx

  v4 = &this[33 * a2];
  v5 = 0;
  if ( v4[573] <= 0 )
LABEL_5:
    strcmp("mcCityData::LookupHookmanRace - failed to find '%s' in hookman %d", a3, a2);
  v6 = v4 + 575;
  while ( strcasecmp(this[*v6 + 20], a3) )
  {
    ++v5;
    ++v6;
    if ( v5 >= v4[573] )
      goto LABEL_5;
  }
  return v5;
}

```

### `mcUnlocking__IsInAirControlUnlocked_bool_const`
- **MC2 Xbox VA:** `0x1533B0..0x153400` (80 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x4D4810`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_bdb06559d649daab34564ff279b08d47f6b9a04f09bdc5778bc7673e94372da5`

```cpp
char __thiscall mcUnlocking__IsInAirControlUnlocked_bool_const(int *this, char a2)
{
  if ( byte_3AC6E9 == 1 )
    return 1;
  if ( a2 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 7, 0);
  return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 7, 0)
      || mcUnlocking__EvaluateUnlockRule_int_int_const(this, 11, 0);
}

```

## 2. Full Symbol Equivalence Table (146 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x011130` | `0x012440` | `-` | `Main_void` | 509 | 553 | +44 | `seed` |
| `0x01F3F0` | `0x028E50` | `0x5B90C8` | `mcLayerRaceEditor__GetName_void_const` | 16 | 18 | +2 | `seed` |
| `0x01F708` | `0x029200` | `0x1A9C88` | `mcLayerRace__Load_void` | 392 | 11 | -381 | `seed` |
| `0x01FA30` | `0x029B70` | `0x5B9330` | `mcLayerAmbients__GetName_void_const` | 16 | 32 | +16 | `seed` |
| `0x022DF9` | `0x1881A0` | `0x35A190` | `mcMenuRaceEditor__PopulateMenu_void` | 28 | 1131 | +1103 | `seed` |
| `0x03F7A3` | `0x18DD50` | `0x34FFD0` | `mcRaceMgr__UpdateCheckUnplugged_void` | 1277 | 509 | -768 | `seed` |
| `0x0415D0` | `0x15E720` | `0x379990` | `mcNetworkWaiting__DisplayHostLostMessage_net__eQuitReason` | 480 | 197 | -283 | `seed` |
| `0x041E78` | `0x15BE30` | `0x379F98` | `mcNetworkWaiting__FileIO_datParser__ref` | 1032 | 3158 | +2126 | `seed` |
| `0x043B5F` | `0x15EA90` | `0x378588` | `mcNetworkWaitingCountdown__mcNetworkWaitingCountdown_void` | 2385 | 1057 | -1328 | `seed` |
| `0x0477F9` | `0x165ED0` | `0x34BAA0` | `GetTrafficDenString_int` | 820 | 69 | -751 | `seed` |
| `0x047C57` | `0x1851F0` | `0x34D408` | `mcMenuCustomRaceType__GetTeamModeString_int` | 2607 | 69 | -2538 | `seed` |
| `0x04AA44` | `-` | `0x36D250` | `mcNetworkHostSelect__JoinFailed_net__eQuitReason` | 192 | 0 | +0 | `ps2_callgraph` |
| `0x055F60` | `0x15E320` | `-` | `mcNetworkWaiting__Show_bool` | 96 | 83 | -13 | `insn_signature` |
| `0x063850` | `0x15DDB0` | `0x3772C0` | `mcNetworkWaiting__mcNetworkWaiting_char_const__ptr__int` | 266 | 1008 | +742 | `seed` |
| `0x0673B0` | `0x34D890` | `-` | `mcUiKeyboard__StripLeadingAndTrailingSpaces_char__ptr__int_char_const__ptr` | 112 | 104 | -8 | `insn_signature` |
| `0x091370` | `0x19D980` | `0x395460` | `mcPropType__LoadTypeData_char_const__ptr__char_const__ptr` | 3072 | 4975 | +1903 | `seed` |
| `0x096DA8` | `0x16ADD0` | `0x358C40` | `mcMenuPause__DoMoveToNextRace_void` | 2109 | 1870 | -239 | `seed` |
| `0x098186` | `0x16BFA0` | `0x35AA10` | `mcMenuRaceOver__PopulateMenu_int` | 550 | 2721 | +2171 | `seed` |
| `0x0983AC` | `0x16B51E` | `0x34FFD0` | `mcMenuRaceOver__HandleCareerAndCruiseSelection_int` | 2071 | 802 | -1269 | `career_semantic_seed` |
| `0x09B910` | `0x1CD0C0` | `0x3D1B28` | `aiRaceShortcut__CalculateLength_void` | 224 | 211 | -13 | `seed` |
| `0x09BDA0` | `0x1CA6E0` | `0x3D5A30` | `mcRaceBase__LoadResetPosition_void` | 496 | 530 | +34 | `seed` |
| `0x09BF90` | `0x1CA900` | `-` | `mcRaceBase__LoadWeather_datAsciiTokenizer__ref` | 384 | 228 | -156 | `seed` |
| `0x09C3F0` | `0x1CAEF0` | `0x3D7960` | `mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref` | 336 | 331 | -5 | `seed` |
| `0x09C540` | `0x1CB040` | `0x3D7B80` | `mcRaceBase__LoadOpponentPersonality_int_datAsciiTokenizer__ref` | 512 | 523 | +11 | `seed` |
| `0x09C830` | `0x1CB380` | `0x3D8820` | `mcRaceBase__LoadAmbientRoadOverride_datAsciiTokenizer__ref` | 336 | 334 | -2 | `seed` |
| `0x09C980` | `0x1CB4D0` | `0x3D89F0` | `mcRaceBase__LoadClosedRoads_datAsciiTokenizer__ref` | 144 | 126 | -18 | `seed` |
| `0x09CA10` | `0x1D1440` | `0x3D8F30` | `mcRaceBase__LoadPreRaceCam_datAsciiTokenizer__ref` | 256 | 204 | -52 | `seed` |
| `0x09DAE0` | `0x1A1760` | `0x3DDA08` | `mcRaceOver__CheckAndShowUnlockedCar_void` | 384 | 416 | +32 | `career_semantic_seed` |
| `0x09DC60` | `0x1A1760` | `0x3DDA08` | `mcRaceOver__CheckAndShowUnlockedAbilities_void` | 336 | 416 | +80 | `career_semantic_seed` |
| `0x09E5E0` | `0x1D2150` | `0x3D1840` | `aiRaceShortcut__LoadShortcut_datAsciiTokenizer__ref` | 304 | 335 | +31 | `seed` |
| `0x09E9A0` | `0x1CDC80` | `-` | `mcRaceBase__LoadCheckpoints_datAsciiTokenizer__ref` | 800 | 667 | -133 | `seed` |
| `0x09ECC0` | `0x1D4CA0` | `0x3D7F88` | `mcRaceBase__LoadPathFindingShortcuts_datAsciiTokenizer__ref` | 144 | 123 | -21 | `seed` |
| `0x0A13F0` | `0x1D28C0` | `0x3D1288` | `aiOpponentStart__LoadPreRacePath_datAsciiTokenizer__ref` | 64 | 103 | +39 | `seed` |
| `0x0A1790` | `0x1D5A30` | `0x3D7EB8` | `mcRaceBase__LoadPathFindingShortcuts_char_const__ptr__char_const__ptr` | 176 | 163 | -13 | `seed` |
| `0x0A26A0` | `0x1D3AE0` | `0x3D6ED8` | `mcRaceBase__LoadOpponents_datAsciiTokenizer__ref` | 1552 | 2116 | +564 | `seed` |
| `0x0A3370` | `0x13A690` | `0x33EC20` | `mcMenuArcade__GetRaceTypeName_int_int` | 187 | 214 | +27 | `seed` |
| `0x0A34F0` | `0x1D4F20` | `0x3D4A20` | `mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref` | 475 | 2832 | +2357 | `career_semantic_seed` |
| `0x0A379D` | `0x1D4F20` | `0x3D4A20` | `mcRaceBase__Load_datAsciiTokenizer__ref__mcRaceBase__ptr` | 1539 | 2818 | +1279 | `seed` |
| `0x0A43F0` | `0x1E06E0` | `0x3F4D60` | `mcRaceCheckpoint__PlayerFinished_int` | 1104 | 1585 | +481 | `seed` |
| `0x0ADDA0` | `0x1D7AB0` | `0x3E8248` | `mcRaceHookmen__PostLevelLoad_void` | 368 | 320 | -48 | `career_callgraph` |
| `0x0AE2C0` | `0x1D75A0` | `0x3E7660` | `mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int` | 576 | null | +null | `career_callgraph` |
| `0x0AE500` | `0x1D7780` | `0x3E7C58` | `mcRaceHookmen__PlayerFinishedFollow_void` | 160 | null | +null | `career_semantic_seed` |
| `0x0AEA80` | `0x1D6D70` | `0x3E8248` | `mcRaceHookmen__LoadAllHookmanSubRaces_void` | 368 | 560 | +192 | `career_callgraph` |
| `0x0AEEF0` | `0x1D7C00` | `0x3E7588` | `mcRaceHookmen__Update_void` | 1024 | null | +null | `career_callgraph` |
| `0x0AF2F0` | `0x1D6D70` | `0x3E8710` | `mcRaceHookmen__Load_char_const__ptr__char_const__ptr` | 176 | 560 | +384 | `career_semantic_seed` |
| `0x0B0010` | `0x1D5AE0` | `0x3D0510` | `mcRaceAmbient__Load_datAsciiTokenizer__ref` | 32 | 23 | -9 | `seed` |
| `0x0B0030` | `0x1D5B00` | `0x3D0F88` | `mcRaceAmbient__FindMotionPathType_datAsciiTokenizer__ref` | 80 | 79 | -1 | `seed` |
| `0x0B0170` | `0x1D5B70` | `0x3D0708` | `mcRaceAmbient__LoadProperties_datAsciiTokenizer__ref` | 160 | 148 | -12 | `seed` |
| `0x0B02F0` | `0x1D5D80` | `0x3D0318` | `mcRaceAmbient__mcRaceAmbient_void` | 272 | 275 | +3 | `seed` |
| `0x0B0440` | `0x1D5F10` | `0x3D08B8` | `mcRaceAmbient__LoadPathNodes_datAsciiTokenizer__ref` | 416 | 423 | +7 | `seed` |
| `0x0B05E0` | `0x1D60C0` | `0x3D0540` | `mcRaceAmbient__Load_datAsciiTokenizer__ref__char_const__ptr__char_const__ptr` | 77 | 316 | +239 | `prop_round_1` |
| `0x0B0850` | `0x227B90` | `0x465FC0` | `mcCreatureManager__LoadRaceStarterData_datAsciiTokenizer__ref__mcCreatureAnimMgr__ref__bool` | 1008 | 504 | -504 | `seed` |
| `0x0B18A0` | `0x156C90` | `0x341DF8` | `mcMenuBrain__CreateWidgets_bool_bool` | 304 | 6714 | +6410 | `seed` |
| `0x0BE780` | `0x0B7D30` | `-` | `mcRaceBase__FileIO_datParser__ref` | 48 | 5 | -43 | `prop_round_2` |
| `0x0C4D20` | `-` | `0x407D68` | `aiPathGraph__ClearGraph_void` | 80 | 0 | +0 | `ps2_callgraph` |
| `0x0C5250` | `0x26FE80` | `0x407E48` | `aiPathGraph__Reset_void` | 16 | 186 | +170 | `prop_round_1` |
| `0x0C5260` | `0x1E6360` | `0x4080A0` | `aiPathGraph__Load_datAsciiTokenizer__ref__mcRaceBase__ptr` | 1072 | 650 | -422 | `seed` |
| `0x0C5720` | `0x1E6CB0` | `0x3FE820` | `mcHeliRace__Load_datAsciiTokenizer__ref` | 32 | 23 | -9 | `seed` |
| `0x0C5740` | `0x1E6C20` | `0x3FE848` | `mcHeliRace__LoadProperties_datAsciiTokenizer__ref` | 144 | 129 | -15 | `seed` |
| `0x0C57D0` | `-` | `0x3FEDA8` | `aiCopHeli__SetHeliPosition_Vector3_const__ref` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x0C5870` | `0x2B7F50` | `0x3FF360` | `aiCopHeli__SetRailRecoveryParameters_void` | 80 | 504 | +424 | `seed` |
| `0x0C58C0` | `-` | `0x3FF3D8` | `aiCopHeli__ComputePathSpeedParameters_void` | 384 | 0 | +0 | `ps2_callgraph` |
| `0x0C6C00` | `-` | `0x3FF310` | `aiCopHeli__SetPathRecoveryParameters_void` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x0C6D00` | `-` | `0x3FF2D0` | `aiCopHeli__SetSearchPathType_aiCopHeli__TSearchPathType` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x0C6E10` | `0x1E8870` | `0x3FEC20` | `aiCopHeli__Reset_void` | 192 | 220 | +28 | `seed` |
| `0x0C6F30` | `0x1E89C0` | `0x3FE910` | `aiCopHeli__aiCopHeli_void` | 544 | 652 | +108 | `seed` |
| `0x0C7370` | `0x1EB540` | `0x3FDE28` | `aiBrainHookman__PreUpdate_void` | 142 | 1232 | +1090 | `career_callgraph` |
| `0x0C73FE` | `0x1EBA20` | `0x3FDDC8` | `aiBrainHookman__Update_void` | 930 | 1056 | +126 | `career_callgraph` |
| `0x0C77A0` | `0x1EC140` | `0x3FE580` | `aiBrainHookman__RestartCruise_void` | 304 | 272 | -32 | `career_semantic_seed` |
| `0x0C7940` | `0x1EC250` | `0x3FE810` | `aiBrainHookman__IsEngagedAndReadyForRace_void_const` | 48 | 464 | +416 | `career_callgraph` |
| `0x0C7E90` | `0x1ED090` | `0x404988` | `aiOpponent__FileIO_datParser__ref` | 16 | 396 | +380 | `seed` |
| `0x0C7EA0` | `0x1ED230` | `0x404998` | `aiOpponent__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0C7EB0` | `0x1ED240` | `0x4049A8` | `aiOpponent__FileIO_datParser__ref` | 160 | 147 | -13 | `seed` |
| `0x0D24C0` | `0x1EE680` | `0x5C7EC8` | `aiStateChase__GetName_void_const` | 16 | 145 | +129 | `seed` |
| `0x0D2BF0` | `0x1EF4F0` | `0x5C8238` | `aiState__GetName_void_const` | 16 | 77 | +61 | `seed` |
| `0x0D32E0` | `0x1F1480` | `0x5C7FF0` | `aiStatePatrolRoute__GetName_void_const` | 16 | 25 | +9 | `seed` |
| `0x0D8F20` | `0x1F2B40` | `0x5C8060` | `aiStateShortcutDrive__GetName_void_const` | 16 | 46 | +30 | `seed` |
| `0x0D91A0` | `0x1F2F10` | `0x5C7EB8` | `aiStateBlock__GetName_void_const` | 16 | 25 | +9 | `seed` |
| `0x0D9A30` | `0x1F39F0` | `0x5C7F88` | `aiStatePatrol__GetName_void_const` | 16 | 31 | +15 | `seed` |
| `0x0DA620` | `0x1F4950` | `0x5C7F28` | `aiStateIdle__GetName_void_const` | 16 | 25 | +9 | `seed` |
| `0x0E8400` | `0x10A7F0` | `0x5BE410` | `opponentTuneStaticData__GetTypeName_void` | 16 | 27 | +11 | `seed` |
| `0x0E8410` | `0x10A820` | `0x2F0F28` | `opponentTuneStaticData__FileIO_datParser__ref` | 256 | 242 | -14 | `seed` |
| `0x0E8510` | `0x10A920` | `0x2F0D08` | `opponentTuneStaticData__opponentTuneStaticData_void` | 448 | 641 | +193 | `seed` |
| `0x0E86F0` | `0x10ABE0` | `-` | `opponentIconTuneData__InitStaticData_void` | 64 | 50 | -14 | `insn_signature` |
| `0x0F6C60` | `0x10E800` | `0x2F3950` | `mcPowerUpTypeDisrupter__mcPowerUpTypeDisrupter_void` | 48 | 34 | -14 | `seed` |
| `0x0F7B80` | `0x110050` | `0x2F6020` | `mcPowerUpTypeDecoy__mcPowerUpTypeDecoy_void` | 32 | 30 | -2 | `seed` |
| `0x0FC950` | `0x069ED0` | `-` | `aiAmbientTrafficData__FileIO_datParser__ref` | 80 | 71 | -9 | `insn_signature` |
| `0x0FCB00` | `0x069FA0` | `0x21AEE8` | `aiAmbientTrafficData__FileIO_datParser__ref` | 128 | 63 | -65 | `seed` |
| `0x100530` | `0x07FC00` | `0x22F070` | `mcTrainManager__LoadCityTrains_char_const__ptr` | 272 | 252 | -20 | `seed` |
| `0x1049C0` | `0x077AE0` | `0x22D0C0` | `aiAmbientVehicle__CreateSmoke_void` | 1427 | 1312 | -115 | `seed` |
| `0x10A2C0` | `-` | `0x22E658` | `mcAmbientControlledPath__SetToStart_void` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x10A2E0` | `-` | `0x22E740` | `mcAmbientControlledPath__GetInitialStart_void_const` | 14 | 0 | +0 | `ps2_callgraph` |
| `0x10A310` | `0x081B40` | `0x22E618` | `mcAmbientControlledPath__mcAmbientControlledPath_void` | 32 | 31 | -1 | `seed` |
| `0x10A3F0` | `-` | `0x22E838` | `mcAmbientControlledPath__SetClosestNodeAsCurrentStart_Vector3_const__ref` | 144 | 0 | +0 | `ps2_callgraph` |
| `0x10A510` | `0x07B720` | `0x21F778` | `aiAmbientType__SetVehicleClass_void` | 192 | 102 | -90 | `seed` |
| `0x10A89F` | `0x07C736` | `0x221C10` | `aiAmbientType__FileIO_datParser__ref` | 801 | 670 | -131 | `seed` |
| `0x10B3A0` | `0x07CF60` | `-` | `aiAmbientType__LoadAndInitialization_short` | 2624 | 1991 | -633 | `seed` |
| `0x10C810` | `0x07FDA0` | `0x231428` | `mcAmbientDistrib__LoadHeader_datAsciiTokenizer__ref` | 208 | 211 | +3 | `seed` |
| `0x10DA80` | `0x081E70` | `0x22FCA0` | `mcTrainType__Init_char_const__ptr` | 512 | 607 | +95 | `seed` |
| `0x10E530` | `0x07AAE0` | `0x213588` | `mcTrainSegment__Init_mcTrainType__ref` | 256 | 461 | +205 | `seed` |
| `0x10EC80` | `0x082520` | `0x232BA8` | `mcTrainBuilder__FindTrainType_char_const__ptr` | 128 | 126 | -2 | `seed` |
| `0x10ED00` | `-` | `0x233148` | `mcTrainBuilder__GetTrainTrack_int_const` | 16 | 0 | +0 | `ps2_callgraph` |
| `0x10EDF0` | `0x0827B8` | `0x2328C8` | `mcTrainBuilder__LoadTrainSegments_mcTrain__ref__datBaseTokenizer__ref` | 304 | 424 | +120 | `seed` |
| `0x10F120` | `0x082C80` | `0x232430` | `mcTrainBuilder__LoadTrainTypes_char_const__ptr` | 352 | 352 | +0 | `seed` |
| `0x110C80` | `0x2B7C60` | `0x5017F0` | `aiRailNetwork__GetRoad_int_const` | 16 | 15 | -1 | `seed` |
| `0x110CA0` | `0x2B7C80` | `0x501820` | `aiRailNetwork__GetTrafficControl_int_const` | 16 | 15 | -1 | `seed` |
| `0x111FF0` | `-` | `0x4FEE58` | `aiObstacleGrid__GetCellIndex_int__ref__int__ref__Vector3_const__ref__const` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x1126D0` | `0x2B7330` | `0x4FF9B0` | `aiObstacleGrid__Detach_aiObstacle__ptr` | 112 | 110 | -2 | `seed` |
| `0x112770` | `0x2B7440` | `0x4FEE30` | `aiObstacleGrid__GetCellIndex_Vector3_const__ref__const` | 32 | 111 | +79 | `seed` |
| `0x112790` | `0x2B74B0` | `0x4FF8F8` | `aiObstacleGrid__Attach_aiObstacle__ptr` | 96 | 100 | +4 | `seed` |
| `0x112880` | `0x2B97F0` | `0x5035A0` | `aiRailNetwork__FindVerifiedRoadId_Vector3_const__ref__const` | 144 | 160 | +16 | `seed` |
| `0x112CD0` | `0x2B99A0` | `0x503448` | `aiRailNetwork__LoadOverridenRoad_datAsciiTokenizer__ref` | 217 | 213 | -4 | `seed` |
| `0x112FD0` | `0x2B9A80` | `0x5032F8` | `aiRailNetwork__LoadRailNetworkOverrides_char_const__ptr` | 256 | 242 | -14 | `seed` |
| `0x113150` | `0x2B9C00` | `0x503798` | `aiRailNetwork__LoadRailNetwork_char_const__ptr` | 1536 | 1452 | -84 | `seed` |
| `0x1166B0` | `0x2B9420` | `0x504438` | `aiRoad__SetLoadOverrides_Vector3_const__ref__Vector3_const__ref__float_float` | 112 | 148 | +36 | `seed` |
| `0x116F20` | `0x2B94E0` | `0x5044C8` | `aiRoad__SetFlag_unsigned_int` | 48 | 54 | +6 | `seed` |
| `0x123DB0` | `0x334EB0` | `0x566700` | `mcRain__FileIO_datParser__ref` | 576 | 563 | -13 | `seed` |
| `0x124192` | `0x3350F0` | `0x564960` | `mcRain__mcRain_void` | 398 | 795 | +397 | `seed` |
| `0x14DF10` | `-` | `-` | `mcConfig__ParseStartupAndRaceCommandLineParams_void` | 1616 | null | +null | `career_semantic_seed` |
| `0x14E6A0` | `0x26AF20` | `0x4BE508` | `mcRaceConfig__SetTOD_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E6F0` | `0x26AF70` | `0x4BE598` | `mcRaceConfig__SetRaceType_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E740` | `0x26AFC0` | `0x4BE628` | `mcRaceConfig__SetWeather_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E790` | `0x26B050` | `0x4BE708` | `mcRaceConfig__SetCity_char_const__ptr` | 80 | 80 | +0 | `seed` |
| `0x14EB40` | `0x26B770` | `0x4BE1C8` | `mcRaceConfig__LoadInfo_datAsciiTokenizer__ref` | 320 | 358 | +38 | `seed` |
| `0x14ED80` | `0x26BAB0` | `0x4BE0D0` | `mcRaceConfig__LoadRaceInfo_void` | 208 | 205 | -3 | `seed` |
| `0x14EFF0` | `0x27D350` | `0x4C8990` | `mcProgressManager__IsRaceBeaten_int_int_const` | 96 | 240 | +144 | `career_callgraph` |
| `0x14F560` | `0x276FC0` | `0x4C0060` | `mcProgressManager__SelectHookmanRaceFromFollow_int_int` | 80 | 160 | +80 | `career_callgraph` |
| `0x14F5F0` | `0x277350` | `0x4C02C0` | `mcProgressManager__UpdateHookmanRacesCompleted_int_int` | 112 | 240 | +128 | `career_callgraph` |
| `0x14F770` | `0x277CA0` | `0x4C0708` | `mcProgressManager__MarkRaceAsBeaten_int_int` | 192 | 384 | +192 | `career_semantic_seed` |
| `0x14F8C0` | `0x277760` | `0x4C00C8` | `mcProgressManager__CheckAndRequestPostRaceMovie_int_int` | 304 | 464 | +160 | `career_callgraph` |
| `0x14F9F0` | `0x2774B0` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreRaceMovie_int_int` | 144 | 128 | -16 | `career_callgraph` |
| `0x14FAF0` | `0x278270` | `0x4BFBD8` | `mcProgressManager__SetupNextCareerRace_void` | 352 | 272 | -80 | `career_semantic_seed` |
| `0x14FCC0` | `0x277EE0` | `0x4BFDB0` | `mcProgressManager__ReportRaceResult_int` | 304 | 512 | +208 | `career_semantic_seed` |
| `0x14FF10` | `0x26DA10` | `0x4B7B20` | `mc__mcCityData__LookupHookmanRace_char_const__ptr__int` | 128 | 96 | -32 | `career_semantic_seed` |
| `0x1504A0` | `0x26D430` | `-` | `mc__LookupRaceType_char_const__ptr` | 80 | 66 | -14 | `seed` |
| `0x150820` | `0x26D4B0` | `0x4B9870` | `mc__ConvertTrafficDensityEnumToFloat_mc__eTrafficDensity` | 80 | 65 | -15 | `seed` |
| `0x150FA0` | `-` | `-` | `mc__LookupRaceAcrossCities_char_const__ptr__int__ref__int__ref` | 64 | null | +null | `career_callgraph` |
| `0x1533B0` | `-` | `0x4D4810` | `mcUnlocking__IsInAirControlUnlocked_bool_const` | 80 | null | +null | `career_callgraph` |
| `0x15E660` | `0x203BF0` | `0x5CA3A0` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___find_uiStaticString_const__ref` | 128 | 126 | -2 | `prop_round_2` |
| `0x15FA30` | `0x205350` | `0x5C8B40` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_atPtr_uiWidget__Select1st_pair_uiStaticString_const_atPtr_uiWidget_less_uiStaticString_allocator_atPtr_uiWidget___insert_unique_pair_uiStaticString_const_atPtr_uiWidget_const__ref` | 272 | 285 | +13 | `prop_round_4` |
| `0x15FB40` | `0x205470` | `0x5C9090` | `_Rb_tree_unsigned_int_pair_unsigned_int_const_atPtr_uiWidget__Select1st_pair_unsigned_int_const_atPtr_uiWidget_less_unsigned_int_allocator_atPtr_uiWidget___insert_unique_pair_unsigned_int_const_atPtr_uiWidget_const__ref` | 192 | 185 | -7 | `prop_round_4` |
| `0x15FC00` | `0x205590` | `0x5CA818` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___insert_unique_pair_uiStaticString_const_unsigned_int_const__ref` | 272 | 285 | +13 | `prop_round_2` |
| `0x175F80` | `0x0ADEE0` | `0x262510` | `vehDrivetrainTune__FileIO_datParser__ref` | 80 | 76 | -4 | `seed` |
| `0x190350` | `0x2A5340` | `0x4D95C0` | `phArchetypeDamp__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 432 | 496 | +64 | `seed` |
| `0x1F17B0` | `0x2D7470` | `-` | `gfxLoadTargaImage_char_const__ptr__bool` | 576 | 575 | -1 | `seed` |
| `0x3080D0` | `0x4168B0` | `-` | `XDK::D3D_KickOffAndWaitForIdle` | 32 | 17 | -15 | `insn_signature` |
