# REA Dossier: Props, Collision Bounds & Physics Archetypes (`props_and_bounds`)

- **REA Evidence ID:** `ev_561d63745141ec33742860f68db0a2c8641603efc010627d1f6641eab513656e`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 102
- **Hex-Rays Decompiled Functions:** 14

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

### `mcPropType__LoadTuneData_void`
- **MC2 Xbox VA:** `0x091000..0x910b6` (192 B) | **MC3 Xbox VA:** `0x19D4B0` (765 B, delta: `+573 B`) | **MC3 PS2 VA:** `0x396770`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_828704c03de126e3afb985798d6de8f0f9218e4d209b4f4b88821367f06e192a`

```cpp
// positive sp value has been detected, the output may be wrong!
int __userpurge mcPropType__LoadTuneData_void@<eax>(int a1@<edx>, int a2@<ebx>, int a3@<esi>, char a4, char a5)
{
  int v6; // [esp-19Ch] [ebp-19Ch] BYREF
  int v7; // [esp-198h] [ebp-198h] BYREF

  (*(void (__cdecl **)(int *))(a1 + 12))(&v7);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("LockPitch", 1) )
    *(_BYTE *)(a3 + 308) |= 4u;
  datBaseTokenizer__CheckToken_char_const__ptr__bool("}", 1);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("SparkSound", 1)
    && (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("{", 1)
    || (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("ParticleSound", 1)
    && (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("{", 1) )
  {
    (*(void (__thiscall **)(_DWORD, int *))(**(_DWORD **)(a3 + 304) + 12))(*(_DWORD *)(a3 + 304), &v6);
  }
  datBaseTokenizer__CheckToken_char_const__ptr__bool("}", 1);
  return ((int (__thiscall *)(int))Stream__Close_void)(a2);
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

### `mcArchetypeBreak__LoadData_datAsciiTokenizer__ref__phBound__ptr`
- **MC2 Xbox VA:** `0x091F90..0x92026` (160 B) | **MC3 Xbox VA:** `0x0EEDF0` (199 B, delta: `+39 B`) | **MC3 PS2 VA:** `0x2BF3A8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_9bd86cd3649de3636cc4343e520de2f6b4c8bd227e6580c45531adc96a7a4448`

```cpp
void __thiscall mcArchetypeBreak__LoadData_datAsciiTokenizer__ref__phBound__ptr(int this, int a2, int a3)
{
  phArchetypeDamp__LoadData_datAsciiTokenizer__ref__phBound__ptr(a2, a3);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("impactThreshold:", 1) )
    *(_WORD *)(this + 144) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("disappearsAfterBreak:", 1) )
    *(_WORD *)(this + 146) = (*(int (__thiscall **)(int))(*(_DWORD *)a2 + 16))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Friction:", 1) )
    *(float *)(this + 192) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("Elasticity:", 1) )
    *(float *)(this + 188) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a2 + 20))(a2);
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

### `mc__LookupHookman_char_const__ptr__int__ref__int__ref`
- **MC2 Xbox VA:** `0x1504F0..0x150531` (80 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x4B96F0`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_a516a8c91f367a71b363284711e1043b19ff87ba649666f846e14f020abbf4ac`

```cpp
char __cdecl mc__LookupHookman_char_const__ptr__int__ref__int__ref(int a1, _DWORD *a2, int a3)
{
  int v3; // edi
  char **v4; // esi
  char result; // al

  v3 = 0;
  v4 = off_34F4F8;
  while ( 1 )
  {
    result = sub_14FF90(a1, a3);
    if ( result )
      break;
    v4 += 1182;
    ++v3;
    if ( (int)v4 >= (int)off_353ED8 )
      return result;
  }
  *a2 = v3;
  return 1;
}

```

### `phArchetypeMgr__RegisterArchetype_phBound__ptr__char_const__ptr__bool_int_float`
- **MC2 Xbox VA:** `0x181550..0x181623` (224 B) | **MC3 Xbox VA:** `0x2A03A0` (241 B, delta: `+17 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `insn_signature` | **REA Function Evidence ID:** `ev_717372348405454f6a606d59147638be743c5d74d7644de5ca539e83495bddb1`

```cpp
int __stdcall phArchetypeMgr__RegisterArchetype_phBound__ptr__char_const__ptr__bool_int_float(
        int a1,
        int a2,
        char a3,
        int a4,
        float a5)
{
  int v5; // esi
  int v6; // eax
  int v7; // eax
  int v8; // eax

  v5 = sub_190930(a2, a1, aBound);
  if ( !v5 )
  {
    if ( a4 )
    {
      if ( a4 == 1 )
      {
        v7 = _builtin_new(64);
        if ( v7 )
          v5 = sub_1906F0(v7);
        else
          v5 = 0;
        if ( a3 )
          sub_1816C0(a2, v5, a1, a5, a3, 1);
      }
      else if ( a4 == 2 )
      {
        v8 = _builtin_new(144);
        v5 = v8 ? sub_190730(v8) : 0;
        if ( a3 )
          sub_1816C0(a2, v5, a1, a5, a3, 2);
      }
    }
    else
    {
      v6 = _builtin_new(28);
      if ( v6 )
        v5 = sub_1906A0(v6);
      else
        v5 = 0;
    }
  }
  sub_18FA40(a1);
  return sub_181480(v5, a2);
}

```

### `phArchetypeMgr__PostLoadCompute_char_const__ptr__phArchetypePhys__ptr__phBound_const__ptr__float_bool_int`
- **MC2 Xbox VA:** `0x181800..0x1818a2` (224 B) | **MC3 Xbox VA:** `0x2A0550` (529 B, delta: `+305 B`) | **MC3 PS2 VA:** `0x4DA3B8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_9053a97db16b55cd30cbabc9c75596bf96f4f63f54f326ed05bcc8c464311ee8`

```cpp
// positive sp value has been detected, the output may be wrong!
int __userpurge phArchetypeMgr__PostLoadCompute_char_const__ptr__phArchetypePhys__ptr__phBound_const__ptr__float_bool_int@<eax>(
        float a1@<ebx>,
        int a2@<ebp>,
        _DWORD *a3@<edi>,
        int a4@<esi>,
        int a5,
        int a6,
        int a7,
        int a8,
        const char *a9,
        int a10,
        int a11,
        float a12,
        char a13)
{
  double v13; // st7
  int v14; // edx
  int v15; // eax
  int v17; // [esp-6Ch] [ebp-70h]
  int v18; // [esp-5Ch] [ebp-60h] BYREF
  float v19; // [esp-58h] [ebp-5Ch]
  int v20; // [esp-54h] [ebp-58h]
  int v21; // [esp-50h] [ebp-54h]
  int v22; // [esp-38h] [ebp-3Ch] BYREF
  _BYTE v23[48]; // [esp-2Ch] [ebp-30h] BYREF

  do
  {
    strlen(v23, 64, "%s%i", a9, v17);
    phArchetypeMgr__RegisterArchetype_phBound__ptr__char_const__ptr__bool_int_float(
      *(_DWORD *)(a3[21] + 4 * a4--),
      (int)v23,
      a13,
      a2,
      a1);
  }
  while ( a4 >= 0 );
  v13 = ((double (__thiscall *)(_DWORD *))*(_DWORD *)(*a3 + 52))(a3);
  v14 = *a3;
  v19 = v13 * a12 * 1000.0;
  v15 = (*(int (__thiscall **)(_DWORD *, int *, float))(v14 + 56))(a3, &v22, COERCE_FLOAT(LODWORD(v19)));
  v19 = *(float *)v15;
  v20 = *(_DWORD *)(v15 + 4);
  v21 = *(_DWORD *)(v15 + 8);
  (*(void (__thiscall **)(int))(*(_DWORD *)a8 + 48))(a8);
  return (*(int (__thiscall **)(int, int *))(*(_DWORD *)a8 + 52))(a8, &v18);
}

```

### `phArchetype__LoadData_datAsciiTokenizer__ref__phBound__ptr`
- **MC2 Xbox VA:** `0x18FF60..0x190099` (184 B) | **MC3 Xbox VA:** `0x2A4E00` (343 B, delta: `+159 B`) | **MC3 PS2 VA:** `0x4D8B28`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_d4a340e54ea7fde748241d9af0ba7c0a9a4d1047b008ac555739d9530282533f`

```cpp
int __thiscall phArchetype__LoadData_datAsciiTokenizer__ref__phBound__ptr(_DWORD *this, _DWORD *a2, int a3)
{
  char *v4; // edx
  int datAsciiTokenizer__ref; // edi
  int v6; // eax
  int result; // eax
  char v8[128]; // [esp+10h] [ebp-80h] BYREF

  if ( a3 )
  {
    sub_18FA40(a3);
  }
  else
  {
    if ( !(unsigned __int8)datBaseTokenizer__CheckToken_char_const__ptr__bool("boundsource:", 1) )
    {
      v4 = (char *)a2[1];
      goto LABEL_9;
    }
    (*(void (__thiscall **)(_DWORD *, char *, int))(*a2 + 4))(a2, v8, 128);
    if ( !strcasecmp(v8, "file") )
    {
      (*(void (__thiscall **)(_DWORD *, char *, int))(*a2 + 4))(a2, v8, 128);
      v4 = v8;
LABEL_9:
      v6 = sub_19F480(v4);
      sub_18FA40(v6);
      goto LABEL_11;
    }
    if ( strcasecmp(v8, "local") )
      strcmp("phArchetype:Load - boundsource unknown, '%s'", v8);
    (*(void (__thiscall **)(_DWORD *, const char *))(*a2 + 44))(a2, "{");
    datAsciiTokenizer__ref = phBound__Load_datAsciiTokenizer__ref(a2);
    (*(void (__thiscall **)(_DWORD *, const char *))(*a2 + 44))(a2, "}");
    sub_18FA40(datAsciiTokenizer__ref);
  }
LABEL_11:
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("TypeFlags:", 1) )
    this[3] = (*(int (__thiscall **)(_DWORD *))(*a2 + 16))(a2);
  result = datBaseTokenizer__CheckIToken_char_const__ptr__bool("IncludeFlags:", 1);
  if ( (_BYTE)result )
  {
    result = (*(int (__thiscall **)(_DWORD *))(*a2 + 16))(a2);
    this[4] = result;
  }
  return result;
}

```

### `phArchetypePhys__LoadData_datAsciiTokenizer__ref__phBound__ptr`
- **MC2 Xbox VA:** `0x190150..0x1902e0` (400 B) | **MC3 Xbox VA:** `0x2A5060` (441 B, delta: `+41 B`) | **MC3 PS2 VA:** `0x4D9028`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_614ee0472ec3dbf076c7b67cd838cf72e3db07cf4ee950d96ec457123bed4dd9`

```cpp
void __userpurge phArchetypePhys__LoadData_datAsciiTokenizer__ref__phBound__ptr(
        int a1@<ecx>,
        double a2@<st0>,
        _DWORD *a3,
        int a4)
{
  int v6; // ecx
  double v7; // st7
  int v8; // ecx
  double v9; // st7
  double v10; // st6
  double v11; // st5
  double v12; // st5
  int v13; // ecx
  _DWORD *v14; // eax
  double v15; // st7
  float v16; // [esp+8h] [ebp-Ch] BYREF
  float v17; // [esp+Ch] [ebp-8h]
  float v18; // [esp+10h] [ebp-4h]
  float v19; // [esp+18h] [ebp+4h]
  float v20; // [esp+1Ch] [ebp+8h]
  float v21; // [esp+1Ch] [ebp+8h]

  phArchetype__LoadData_datAsciiTokenizer__ref__phBound__ptr((_DWORD *)a1, a3, a4);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("mass:", 1) )
  {
    (*(void (__thiscall **)(_DWORD *))(*a3 + 20))(a3);
  }
  else
  {
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("density:", 1) )
    {
      v20 = ((double (__thiscall *)(_DWORD *))*(_DWORD *)(*a3 + 20))(a3);
      v6 = *(_DWORD *)(a1 + 8);
      if ( !v6 )
        goto LABEL_10;
      v7 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)v6 + 52))(v6) * v20;
    }
    else
    {
      v8 = *(_DWORD *)(a1 + 8);
      if ( !v8 )
        goto LABEL_10;
      v7 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)v8 + 52))(v8) * flt_354220;
    }
    a2 = v7 * 1000.0;
  }
  *(float *)(a1 + 28) = a2;
LABEL_10:
  (*(void (__thiscall **)(int, _DWORD))(*(_DWORD *)a1 + 48))(a1, *(_DWORD *)(a1 + 28));
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("angInertia:", 1) )
  {
    (*(void (__thiscall **)(_DWORD *, int))(*a3 + 36))(a3, a1 + 36);
  }
  else if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("inertiaBox:", 1) )
  {
    (*(void (__thiscall **)(_DWORD *, float *))(*a3 + 36))(a3, &v16);
    v9 = *(float *)(a1 + 28) * 0.083333336;
    v10 = v18 * v18;
    v11 = v17 * v17;
    v19 = v11;
    *(float *)(a1 + 36) = (v11 + v10) * v9;
    v12 = v16 * v16;
    v21 = v12;
    *(float *)(a1 + 40) = (v12 + v10) * v9;
    *(float *)(a1 + 44) = (v21 + v19) * v9;
  }
  else
  {
    v13 = *(_DWORD *)(a1 + 8);
    if ( v13 )
    {
      v14 = (_DWORD *)(*(int (__thiscall **)(int, float *, _DWORD))(*(_DWORD *)v13 + 56))(
                        v13,
                        &v16,
                        *(_DWORD *)(a1 + 28));
      *(_DWORD *)(a1 + 36) = *v14;
      *(_DWORD *)(a1 + 40) = v14[1];
      *(_DWORD *)(a1 + 44) = v14[2];
    }
    if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("inertiaScale:", 1) )
    {
      v15 = ((double (__thiscall *)(_DWORD *))*(_DWORD *)(*a3 + 20))(a3);
      *(float *)(a1 + 36) = v15 * *(float *)(a1 + 36);
      *(float *)(a1 + 40) = v15 * *(float *)(a1 + 40);
      *(float *)(a1 + 44) = v15 * *(float *)(a1 + 44);
    }
  }
  (*(void (__thiscall **)(int, int))(*(_DWORD *)a1 + 52))(a1, a1 + 36);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("gravityFactor:", 1) )
    *(float *)(a1 + 60) = ((double (__thiscall *)(_DWORD *))*(_DWORD *)(*a3 + 20))(a3);
}

```

### `phBound__Load_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x19EAD0..0x19ecef` (544 B) | **MC3 Xbox VA:** `0x234DF0` (599 B, delta: `+55 B`) | **MC3 PS2 VA:** `0x47E630`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_0faa4a5e63fe87ce0e3b46e1b9ade23931d71bd8b49406fc671b51e7b5cb61c8`

```cpp
void (__thiscall ***__cdecl phBound__Load_datAsciiTokenizer__ref(int a1))(_DWORD, int)
{
  int v1; // eax
  int v2; // eax
  int v3; // eax
  int v4; // eax
  int v5; // eax
  int v6; // eax
  int v7; // eax
  void (__thiscall ***v8)(_DWORD, int); // esi
  _BYTE v10[32]; // [esp+10h] [ebp-20h] BYREF

  datBaseTokenizer__MatchToken_char_const__ptr("version:");
  (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a1 + 4))(a1, v10, 30);
  if ( strcasecmp(v10, "1.01") && (!strcasecmp(v10, &off_33A87C) || !strcasecmp(v10, "1.10")) )
  {
    datBaseTokenizer__MatchToken_char_const__ptr("type:");
    (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a1 + 4))(a1, v10, 30);
    if ( !strcasecmp(v10, "BOX") )
    {
      v1 = _builtin_new(432);
      if ( !v1 )
        return 0;
      v2 = phBoundBox__phBoundBox_void(v1);
LABEL_25:
      v8 = (void (__thiscall ***)(_DWORD, int))v2;
      if ( !v2 || (unsigned __int8)sub_1A4F70(a1, 110) )
        return v8;
      (**v8)(v8, 1);
      return 0;
    }
    if ( !strcasecmp(v10, "SPHERE") )
    {
      if ( !_builtin_new(80) )
        return 0;
      v2 = phBoundSphere__phBoundSphere_float(1065353216);
      goto LABEL_25;
    }
    if ( !strcasecmp(v10, "GEOMETRY") )
    {
      v3 = _builtin_new(140);
      if ( !v3 )
        return 0;
      v2 = phBoundGeometry__phBoundGeometry_void(v3);
      goto LABEL_25;
    }
    if ( !strcasecmp(v10, "HOTDOG") )
    {
      v4 = _builtin_new(88);
      if ( !v4 )
        return 0;
      v2 = phBoundHotdog__phBoundHotdog_void(v4);
      goto LABEL_25;
    }
    if ( !strcasecmp(v10, "OCTREE") )
    {
      v5 = _builtin_new(144);
      if ( !v5 )
        return 0;
      v2 = phBoundOctree__phBoundOctree_void(v5);
      goto LABEL_25;
    }
    if ( !strcasecmp(v10, "QUADTREE") )
    {
      v6 = _builtin_new(144);
      if ( !v6 )
        return 0;
      v2 = phBoundQuadtree__phBoundQuadtree_void(v6);
      goto LABEL_25;
    }
    if ( !strcasecmp(v10, "OTGRID") )
    {
      v7 = _builtin_new(116);
      if ( !v7 )
        return 0;
      v2 = phBoundOTGrid__phBoundOTGrid_void(v7);
      goto LABEL_25;
    }
  }
  return 0;
}

```

### `phBound__LoadFromFile_char_const__ptr`
- **MC2 Xbox VA:** `0x19EF80..0x19f429` (1248 B) | **MC3 Xbox VA:** `0x235050` (1241 B, delta: `-7 B`) | **MC3 PS2 VA:** `0x47E128`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_a292487b8d28976410eb7150f05e8a54968db1dd1a98e6454729f2843b85e25e`

```cpp
void (__thiscall ***__cdecl phBound__LoadFromFile_char_const__ptr(int a1))(_DWORD, int)
{
  int Data_datBinTokenizer__ref__phBound__FileVersion; // eax
  int v2; // ebx
  int v3; // eax
  void (__thiscall ***v4)(_DWORD, int); // esi
  void (__thiscall ***v6)(_DWORD, int); // esi
  int v7; // eax
  int v8; // eax
  int v9; // eax
  int v10; // eax
  int v11; // eax
  int v12; // eax
  int v13; // eax
  int v14; // eax
  int v15; // eax
  int v16; // eax
  int v17; // eax
  int v18; // eax
  int v19; // eax
  int v20; // eax
  _BYTE v21[32]; // [esp+Ch] [ebp-C0h] BYREF
  _DWORD v22[40]; // [esp+2Ch] [ebp-A0h] BYREF

  Data_datBinTokenizer__ref__phBound__FileVersion = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
                                                      "bound",
                                                      a1,
                                                      "bbnd",
                                                      1,
                                                      1);
  v2 = Data_datBinTokenizer__ref__phBound__FileVersion;
  if ( Data_datBinTokenizer__ref__phBound__FileVersion )
  {
    v22[0] = &off_320548;
    datBaseTokenizer__Init_char_const__ptr__Stream__ptr(a1, Data_datBinTokenizer__ref__phBound__FileVersion);
    if ( datBinTokenizer__GetInt_void(v22) == 110 )
    {
      switch ( datBinTokenizer__GetInt_void(v22) )
      {
        case 0:
          if ( !_builtin_new(80) )
            goto LABEL_22;
          v6 = (void (__thiscall ***)(_DWORD, int))phBoundSphere__phBoundSphere_float(1065353216);
          goto LABEL_23;
        case 1:
          v7 = _builtin_new(88);
          if ( !v7 )
            goto LABEL_22;
          v6 = (void (__thiscall ***)(_DWORD, int))phBoundHotdog__phBoundHotdog_void(v7);
          goto LABEL_23;
        case 2:
          v8 = _builtin_new(432);
          if ( !v8 )
            goto LABEL_22;
          v6 = (void (__thiscall ***)(_DWORD, int))phBoundBox__phBoundBox_void(v8);
          goto LABEL_23;
        case 3:
          v9 = _builtin_new(140);
          if ( !v9 )
            goto LABEL_22;
          v6 = (void (__thiscall ***)(_DWORD, int))phBoundGeometry__phBoundGeometry_void(v9);
          goto LABEL_23;
        case 9:
          v10 = _builtin_new(144);
          if ( v10 )
            v6 = (void (__thiscall ***)(_DWORD, int))phBoundOctree__phBoundOctree_void(v10);
          else
LABEL_22:
            v6 = 0;
LABEL_23:
          if ( (unsigned __int8)sub_1A4F90(v22, 110) )
            goto LABEL_70;
          if ( v6 )
            goto LABEL_68;
          goto LABEL_69;
        default:
          Stream__Close_void(v2);
          return 0;
      }
    }
    Stream__Close_void(v2);
    v3 = _builtin_new(140);
    if ( v3 )
      v4 = (void (__thiscall ***)(_DWORD, int))phBoundGeometry__phBoundGeometry_void(v3);
    else
      v4 = 0;
    if ( (unsigned __int8)sub_1B3720(a1, 0) )
      return v4;
    if ( v4 )
      (**v4)(v4, 1);
    return 0;
  }
  v11 = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion("bound", a1, "bnd", 1, 1);
  v2 = v11;
  if ( !v11 )
    return 0;
  v22[0] = &off_33ECE8;
  v22[39] = 0;
  datBaseTokenizer__Init_char_const__ptr__Stream__ptr(a1, v11);
  datBaseTokenizer__MatchToken_char_const__ptr("version:");
  datBaseTokenizer__GetToken_char__ptr__int(v21, 30);
  if ( !strcasecmp(v21, "1.01") )
  {
    Stream__Close_void(v2);
    v12 = _builtin_new(140);
    if ( v12 )
      v4 = (void (__thiscall ***)(_DWORD, int))phBoundGeometry__phBoundGeometry_void(v12);
    else
      v4 = 0;
    if ( (unsigned __int8)phBoundGeometry__Load_char_const__ptr__Vector3_const__ptr(a1, 0) )
      return v4;
    if ( v4 )
      (**v4)(v4, 1);
    return 0;
  }
  if ( strcasecmp(v21, &off_33A87C) && strcasecmp(v21, "1.10") )
    return 0;
  datBaseTokenizer__MatchToken_char_const__ptr("type:");
  datBaseTokenizer__GetToken_char__ptr__int(v21, 30);
  if ( strcasecmp(v21, "SPHERE") )
  {
    if ( !strcasecmp(v21, "HOTDOG") )
    {
      v14 = _builtin_new(88);
      if ( !v14 )
        goto LABEL_69;
      v13 = phBoundHotdog__phBoundHotdog_void(v14);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "BOX") )
    {
      v15 = _builtin_new(432);
      if ( !v15 )
        goto LABEL_69;
      v13 = phBoundBox__phBoundBox_void(v15);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "GEOMETRY") )
    {
      v16 = _builtin_new(140);
      if ( !v16 )
        goto LABEL_69;
      v13 = phBoundGeometry__phBoundGeometry_void(v16);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "OCTREE") )
    {
      v17 = _builtin_new(144);
      if ( !v17 )
        goto LABEL_69;
      v13 = phBoundOctree__phBoundOctree_void(v17);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "QUADTREE") )
    {
      v18 = _builtin_new(144);
      if ( !v18 )
        goto LABEL_69;
      v13 = phBoundQuadtree__phBoundQuadtree_void(v18);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "OTGRID") )
    {
      v19 = _builtin_new(116);
      if ( !v19 )
        goto LABEL_69;
      v13 = phBoundOTGrid__phBoundOTGrid_void(v19);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "FORCESPHERE") )
    {
      v20 = _builtin_new(144);
      if ( !v20 )
        goto LABEL_69;
      v13 = phForceSphere__phForceSphere_void(v20);
      goto LABEL_66;
    }
    if ( !strcasecmp(v21, "COMPOSITE") )
    {
      if ( !_builtin_new(108) )
        goto LABEL_69;
      v13 = sub_1A8D80(0);
      goto LABEL_66;
    }
    return 0;
  }
  if ( !_builtin_new(80) )
    goto LABEL_69;
  v13 = phBoundSphere__phBoundSphere_float(1065353216);
LABEL_66:
  v6 = (void (__thiscall ***)(_DWORD, int))v13;
  if ( !v13 || (unsigned __int8)sub_1A4F70(v22, 110) )
    goto LABEL_70;
LABEL_68:
  (**v6)(v6, 1);
LABEL_69:
  v6 = 0;
LABEL_70:
  Stream__Close_void(v2);
  return v6;
}

```

### `phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion`
- **MC2 Xbox VA:** `0x20AA20..0x20aa5b` (64 B) | **MC3 Xbox VA:** `N/A` (0 B, delta: `+0 B`) | **MC3 PS2 VA:** `0x46CB40`
- **Match Method:** `ps2_callgraph` | **REA Function Evidence ID:** `ev_c8f3a4a30f4721631d77b2fca01fbfb31a37c3a9c7f2a7caaadc89d411358497`

```cpp
int __thiscall phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
        void *this,
        int a2,
        int a3,
        int a4,
        int a5,
        int a6)
{
  int v7; // edi

  (*(void (__thiscall **)(void *, int))(*(_DWORD *)this + 8))(this, a2);
  v7 = (*(int (__thiscall **)(void *, int, int, int, int))(*(_DWORD *)this + 28))(this, a3, a4, a5, a6);
  (*(void (__thiscall **)(void *))(*(_DWORD *)this + 12))(this);
  return v7;
}

```

## 2. Full Symbol Equivalence Table (102 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x01CB42` | `0x024D00` | `0x1B33A8` | `mcNetManagerDerived__PostPeerPhaseChanged_int_net__ePhase` | 142 | 57 | -85 | `seed` |
| `0x020780` | `0x02A2E0` | `0x1A8EC0` | `mcLayerCity__InitPhys_void` | 1104 | 256 | -848 | `seed` |
| `0x063560` | `0x164320` | `0x33B500` | `mcMenuShell__ShowConfirmationSimple_char_const__ptr__unsigned_int_mcMenuMsgBox__MsgItem` | 32 | 64 | +32 | `seed` |
| `0x084D20` | `0x2CE170` | `0x520A28` | `mcCinematicType__FileIO_datParser__ptr` | 112 | 321 | +209 | `seed` |
| `0x084E46` | `0x2CE650` | `0x5216B0` | `mcCinematicCS__FileIO_datParser__ref` | 522 | 357 | -165 | `seed` |
| `0x091000` | `0x19D4B0` | `0x396770` | `mcPropType__LoadTuneData_void` | 192 | 765 | +573 | `seed` |
| `0x091370` | `0x19D980` | `0x395460` | `mcPropType__LoadTypeData_char_const__ptr__char_const__ptr` | 3072 | 4975 | +1903 | `seed` |
| `0x091F90` | `0x0EEDF0` | `0x2BF3A8` | `mcArchetypeBreak__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 160 | 199 | +39 | `seed` |
| `0x0997C0` | `0x161CE0` | `0x33B5D0` | `mcMenuShell__ActivateConfirmation_void` | 574 | 1282 | +708 | `seed` |
| `0x0AC6D0` | `0x1C8B20` | `-` | `phIntersection__Zero_void` | 400 | 550 | +150 | `prop_round_1` |
| `0x0B0170` | `0x1D5B70` | `0x3D0708` | `mcRaceAmbient__LoadProperties_datAsciiTokenizer__ref` | 160 | 148 | -12 | `seed` |
| `0x0C4D20` | `-` | `0x407D68` | `aiPathGraph__ClearGraph_void` | 80 | 0 | +0 | `ps2_callgraph` |
| `0x0C5250` | `0x26FE80` | `0x407E48` | `aiPathGraph__Reset_void` | 16 | 186 | +170 | `prop_round_1` |
| `0x0C5260` | `0x1E6360` | `0x4080A0` | `aiPathGraph__Load_datAsciiTokenizer__ref__mcRaceBase__ptr` | 1072 | 650 | -422 | `seed` |
| `0x0C5740` | `0x1E6C20` | `0x3FE848` | `mcHeliRace__LoadProperties_datAsciiTokenizer__ref` | 144 | 129 | -15 | `seed` |
| `0x0C57D0` | `-` | `0x3FEDA8` | `aiCopHeli__SetHeliPosition_Vector3_const__ref` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x0C5870` | `0x2B7F50` | `0x3FF360` | `aiCopHeli__SetRailRecoveryParameters_void` | 80 | 504 | +424 | `seed` |
| `0x0C58C0` | `-` | `0x3FF3D8` | `aiCopHeli__ComputePathSpeedParameters_void` | 384 | 0 | +0 | `ps2_callgraph` |
| `0x0C6C00` | `-` | `0x3FF310` | `aiCopHeli__SetPathRecoveryParameters_void` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x0C6D00` | `-` | `0x3FF2D0` | `aiCopHeli__SetSearchPathType_aiCopHeli__TSearchPathType` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x0C6E10` | `0x1E8870` | `0x3FEC20` | `aiCopHeli__Reset_void` | 192 | 220 | +28 | `seed` |
| `0x0C6F30` | `0x1E89C0` | `0x3FE910` | `aiCopHeli__aiCopHeli_void` | 544 | 652 | +108 | `seed` |
| `0x10E440` | `0x2A5B50` | `0x4DF3D0` | `phInstBreakable__phInstBreakable_void` | 80 | 39 | -41 | `seed` |
| `0x14FF10` | `0x26DA10` | `0x4B7B20` | `mc__mcCityData__LookupHookmanRace_char_const__ptr__int` | 128 | 96 | -32 | `career_semantic_seed` |
| `0x1504F0` | `-` | `0x4B96F0` | `mc__LookupHookman_char_const__ptr__int__ref__int__ref` | 80 | null | +null | `career_callgraph` |
| `0x152B20` | `0x2923E0` | `-` | `mcPgBinaryRulesEvalBase__RuleOrGroup_const__ptr____lower_bound_mcPgBinaryRulesEvalBase__RuleOrGroup_const__ptr__mcPgBinaryRulesEvalBase__RuleOrGroup_mcPgBinaryRulesEvalBase__RuleOrGroup__Less_int_mcPgBinaryRulesEvalBase__RuleOrG__99c109ff21` | 112 | 109 | -3 | `insn_signature` |
| `0x16CC90` | `0x35E220` | `0x59C558` | `vehDriver__Init_vehSim__ptr__vehDriverTune_const__ptr__Matrix34_const__ptr` | 224 | 257 | +33 | `seed` |
| `0x1769E0` | `0x065FD0` | `-` | `swfINSTANCE__GetProperty_char_const__ptr__swfVARIANT__ref` | 16 | 55 | +39 | `prop_round_3` |
| `0x180290` | `-` | `0x446170` | `crLocalBoneMatrices__Init_int` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x181550` | `0x2A03A0` | `-` | `phArchetypeMgr__RegisterArchetype_phBound__ptr__char_const__ptr__bool_int_float` | 224 | 241 | +17 | `insn_signature` |
| `0x181630` | `0x2A04A0` | `0x4DA188` | `phArchetypeMgr__RegisterNewArchetype_phArchetype__ptr__char_const__ptr` | 144 | 166 | +22 | `seed` |
| `0x181800` | `0x2A0550` | `0x4DA3B8` | `phArchetypeMgr__PostLoadCompute_char_const__ptr__phArchetypePhys__ptr__phBound_const__ptr__float_bool_int` | 224 | 529 | +305 | `seed` |
| `0x18FAA0` | `0x2A4BE0` | `-` | `phArchetype__SetTypeFlag_unsigned_int_bool` | 48 | 40 | -8 | `insn_signature` |
| `0x18FF60` | `0x2A4E00` | `0x4D8B28` | `phArchetype__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 184 | 343 | +159 | `seed` |
| `0x190100` | `0x2A4B70` | `0x4D8DE8` | `phArchetype__Release_bool` | 80 | 62 | -18 | `seed` |
| `0x190150` | `0x2A5060` | `0x4D9028` | `phArchetypePhys__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 400 | 441 | +41 | `seed` |
| `0x190350` | `0x2A5340` | `0x4D95C0` | `phArchetypeDamp__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 432 | 496 | +64 | `seed` |
| `0x190810` | `0x2A5990` | `-` | `phArchetype__Load_datAsciiTokenizer__ref__phBound__ptr` | 119 | 177 | +58 | `insn_signature` |
| `0x191040` | `0x2A4740` | `0x4DEF58` | `phInst__SetArchetype_phArchetype__ptr` | 48 | 47 | -1 | `seed` |
| `0x19DB70` | `-` | `0x4A5B88` | `phQuadtreeCell__phQuadtreeCell_void` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x19DCA0` | `-` | `0x4A5E20` | `phQuadtreeCell__Subdivide_void` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x19E590` | `-` | `0x4A5CB8` | `phQuadtreeCell__ReadCells_datAsciiTokenizer__ref__int` | 240 | 0 | +0 | `ps2_callgraph` |
| `0x19EAD0` | `0x234DF0` | `0x47E630` | `phBound__Load_datAsciiTokenizer__ref` | 544 | 599 | +55 | `seed` |
| `0x19ECF0` | `-` | `0x47E8A8` | `WriteHeader_110_datAsciiTokenizer__ref__phBound__ptr` | 157 | 0 | +0 | `ps2_callgraph` |
| `0x19EF80` | `0x235050` | `0x47E128` | `phBound__LoadFromFile_char_const__ptr` | 1248 | 1241 | -7 | `seed` |
| `0x1A2040` | `0x23BEE0` | `0x49DD90` | `phBoundSphere__CalculateExtents_void` | 144 | 194 | +50 | `prop_round_1` |
| `0x1A31F0` | `0x23D630` | `0x49DBC8` | `phBoundSphere__phBoundSphere_float` | 96 | 84 | -12 | `seed` |
| `0x1A32C0` | `-` | `0x49F870` | `phForceSphere__Zero_void` | 48 | 0 | +0 | `ps2_callgraph` |
| `0x1A4150` | `0x2367C0` | `0x4A1380` | `phForceSphere__Load_v110_datAsciiTokenizer__ref` | 320 | 465 | +145 | `seed` |
| `0x1A4290` | `0x2369A0` | `0x4A15E0` | `phForceSphere__Load_v110_datBinTokenizer__ref` | 288 | 310 | +22 | `seed` |
| `0x1A4570` | `0x236AE0` | `0x49F7F8` | `phForceSphere__phForceSphere_void` | 64 | 116 | +52 | `seed` |
| `0x1A4B80` | `-` | `0x46BAA0` | `phBound__Release_bool` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x1A4FD0` | `0x234C20` | `0x46BA20` | `phBound__phBound_void` | 80 | 71 | -9 | `seed` |
| `0x1A5290` | `0x231930` | `0x4819E8` | `phBoundOTGrid__phBoundOTGrid_void` | 64 | 65 | +1 | `seed` |
| `0x1A53F0` | `0x231B30` | `0x482110` | `phBoundOTGrid__LoadDef_v110_datAsciiTokenizer__ref` | 160 | 151 | -9 | `seed` |
| `0x1A6D80` | `0x233DB0` | `0x475DC0` | `phBoundComposite__SetBound_int_phBound__ptr` | 80 | 52 | -28 | `seed` |
| `0x1A82D0` | `0x2301F0` | `0x475650` | `phBoundComposite__Init_int_phBound__ptr__ptr__Matrix34__ptr` | 160 | 289 | +129 | `seed` |
| `0x1A8480` | `0x2303F0` | `0x475888` | `phBoundComposite__Load_v110_datAsciiTokenizer__ref` | 720 | 897 | +177 | `seed` |
| `0x1A9B80` | `0x24A260` | `0x46DB50` | `phBoundBox__SetSize_Vector3_const__ref` | 176 | 1063 | +887 | `seed` |
| `0x1AE660` | `-` | `0x46D5A8` | `phBoundBox__phBoundBox_void` | 336 | 0 | +0 | `ps2_callgraph` |
| `0x1AE860` | `0x2508F0` | `0x46D8F0` | `phBoundBox__Load_v110_datAsciiTokenizer__ref` | 233 | 298 | +65 | `seed` |
| `0x1B09E0` | `0x239760` | `0x4787E0` | `phBoundGeometry__phBoundGeometry_void` | 80 | 49 | -31 | `seed` |
| `0x1B2078` | `0x2398C0` | `0x478CB0` | `phBoundGeometry__Load_v110_datAsciiTokenizer__ref` | 2333 | 1855 | -478 | `seed` |
| `0x1B29A0` | `0x23A4F0` | `-` | `phBoundGeometry__Load_datAsciiTokenizer__ref__int` | 3454 | 2746 | -708 | `seed` |
| `0x1B3770` | `0x23AFB0` | `-` | `phBoundGeometry__LoadAscii_char_const__ptr__Vector3_const__ptr` | 3433 | 3362 | -71 | `seed` |
| `0x1B44E0` | `0x23BCE0` | `0x479690` | `phBoundGeometry__Load_char_const__ptr__Vector3_const__ptr` | 79 | 29 | -50 | `seed` |
| `0x1BE9B0` | `0x246540` | `0x493E10` | `phBoundQuadtree__phBoundQuadtree_void` | 32 | 29 | -3 | `seed` |
| `0x1BF8A0` | `-` | `0x5CF188` | `phPolytree_phQuadtreeCell___phPolytree_void` | 96 | 0 | +0 | `ps2_callgraph` |
| `0x1BF900` | `-` | `0x5CF1F0` | `phPolytree_phQuadtreeCell___Configure_int_int_int_float` | 128 | 0 | +0 | `ps2_callgraph` |
| `0x1BFDC0` | `-` | `0x5CF2A8` | `phPolytree_phQuadtreeCell___ReadCells_datAsciiTokenizer__ref__phBoundGeometry_const__ptr__int_Vector3_const__ref__Vector3_const__ref` | 144 | 0 | +0 | `ps2_callgraph` |
| `0x1C00F0` | `-` | `0x493EA8` | `phBoundQuadtree__LoadCells_datAsciiTokenizer__ref__int_int_int_int_float_Vector3_const__ref__Vector3_const__ref` | 112 | 0 | +0 | `ps2_callgraph` |
| `0x1C0160` | `0x248020` | `0x493F70` | `phBoundQuadtree__Load_v110_datAsciiTokenizer__ref` | 368 | 394 | +26 | `seed` |
| `0x1C1550` | `0x240980` | `0x47EB78` | `phBoundOctree__phBoundOctree_void` | 32 | 117 | +85 | `seed` |
| `0x1C2C30` | `0x23F080` | `0x47EC70` | `phBoundOctree__LoadCells_datAsciiTokenizer__ref__int_int_int_int_float_Vector3_const__ref__Vector3_const__ref` | 240 | 312 | +72 | `seed` |
| `0x1CB1B0` | `-` | `0x47AA68` | `phBoundHotdog__SetSize_float_float` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x1CB2C0` | `0x251FA0` | `0x47AB28` | `phBoundHotdog__CalculateExtents_void` | 145 | 247 | +102 | `prop_round_1` |
| `0x1CCC90` | `0x2529A0` | `0x47DCD8` | `phBoundHotdog__Load_v110_datAsciiTokenizer__ref` | 256 | 190 | -66 | `seed` |
| `0x1CCFE0` | `0x254240` | `0x47A9F0` | `phBoundHotdog__phBoundHotdog_void` | 96 | 89 | -7 | `seed` |
| `0x1CE3B0` | `0x1A7260` | `-` | `phSurface__SaveData_datAsciiTokenizer__ref` | 16 | 11 | -5 | `prop_round_2` |
| `0x1CE3C0` | `0x1A7270` | `0x3A90A8` | `phSurface__dtor_phSurface_void` | 256 | 238 | -18 | `seed` |
| `0x1CE4C0` | `0x1A7360` | `0x3A9280` | `phSurface__SaveData_datAsciiTokenizer__ref` | 400 | 392 | -8 | `seed` |
| `0x1CE740` | `-` | `0x2C2A20` | `mcPhysicsSurfaceMgr__CreateInstance_void` | 208 | 0 | +0 | `ps2_callgraph` |
| `0x1D1AC0` | `0x1A6BF0` | `-` | `phMaterial__Save_datAsciiTokenizer__ref` | 272 | 255 | -17 | `prop_round_1` |
| `0x1D1BD0` | `-` | `0x3A3410` | `phMaterial__LoadData_datAsciiTokenizer__ref` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x1D1C10` | `0x1A6D30` | `0x3A3488` | `phMaterial__Save_datAsciiTokenizer__ref` | 128 | 113 | -15 | `seed` |
| `0x1D1CB0` | `0x1A6DD0` | `0x3A35A0` | `phMaterial__SaveData_datAsciiTokenizer__ref` | 112 | 101 | -11 | `seed` |
| `0x1D1E10` | `0x1A6F10` | `0x3A3860` | `phMaterialSnd__LoadData_datAsciiTokenizer__ref` | 128 | 151 | +23 | `seed` |
| `0x1D1EC0` | `0x1A6FF0` | `0x3A3970` | `phMaterialSnd__SaveData_datAsciiTokenizer__ref` | 112 | 109 | -3 | `seed` |
| `0x1D2060` | `-` | `0x3A82D0` | `phPolygon__phPolygon_void` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x1D20E0` | `0x1A5730` | `0x3A83D0` | `phPolygon__CalculateNormal_Vector3_const__ptr` | 400 | 605 | +205 | `seed` |
| `0x1D2D00` | `0x1A6620` | `-` | `phPolygon__InitTriangle_unsigned_short_unsigned_short_unsigned_short_Vector3_const__ptr` | 48 | 46 | -2 | `prop_round_1` |
| `0x1D3270` | `0x1A68A0` | `0x3A3FD0` | `phMaterialMgr__GetMaterialIndex_phMaterial_const__ptr` | 48 | 52 | +4 | `seed` |
| `0x1D4880` | `0x20CF20` | `0x4327A0` | `vformatf_char__ptr__int_char_const__ptr__char__ptr` | 80 | 38 | -42 | `seed` |
| `0x1D5770` | `-` | `0x4327C8` | `formatf_char__ptr__int_char_const__ptr___varargs` | 112 | 0 | +0 | `ps2_callgraph` |
| `0x1DF360` | `0x0EAAE0` | `0x2BBAB8` | `txtFontTexGlyph__Load_Stream__ptr` | 112 | 101 | -11 | `seed` |
| `0x1E62B0` | `0x05CE00` | `0x1F6638` | `netAddress__Format_char__ptr__bool_const` | 80 | 81 | +1 | `seed` |
| `0x1EFFD0` | `0x2D8FA0` | `-` | `gfxImage__Create_int_int_gfxImage__gfxImageFormat_int` | 224 | 218 | -6 | `prop_round_1` |
| `0x209740` | `0x20F2C0` | `0x434060` | `datBaseTokenizer__MatchToken_char_const__ptr` | 32 | 26 | -6 | `seed` |
| `0x209760` | `0x20F2E0` | `0x4340A8` | `datBaseTokenizer__MatchIToken_char_const__ptr` | 48 | 47 | -1 | `seed` |
| `0x209B70` | `0x20F7F0` | `-` | `datAsciiTokenizer__MatchInt_char_const__ptr` | 32 | 39 | +7 | `prop_round_1` |
| `0x20AA20` | `-` | `0x46CB40` | `phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x2CECE4` | `0x3C2018` | `-` | `XDK::IDirectSound_EnableHeadphones` | 28 | 28 | +0 | `insn_signature` |
