# REA Dossier: File IO, Parsers, String Tables, Streams & Main Loop (`file_io_and_core`)

- **REA Evidence ID:** `ev_ef5a017f532a152ba6345da853822d0bafe0fd5c95fa9d69b4556c43986b1398`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 276
- **Hex-Rays Decompiled Functions:** 33

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

### `hudMapLocal__SharedDataLocalMap__TextureData__FileIO_datParser__ref__char_const__ptr`
- **MC2 Xbox VA:** `0x0B5820..0xb5956` (320 B) | **MC3 Xbox VA:** `0x0BA0D0` (310 B, delta: `-10 B`) | **MC3 PS2 VA:** `0x287DB0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_1a84499787590fcd437d3d8366a95258d3959cebd674fe7dc01600fc75832cf4`

```cpp
int __thiscall hudMapLocal__SharedDataLocalMap__TextureData__FileIO_datParser__ref__char_const__ptr(
        char *this,
        int a2,
        const char *a3)
{
  _BYTE v5[160]; // [esp+Ch] [ebp-A0h] BYREF

  strlen(v5, 160, "%s.Segment_Witdth", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this, 1, 0);
  strlen(v5, 160, "%s.Segment_Height", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this + 4, 1, 0);
  strlen(v5, 160, "%s.Segment_Border_X", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this + 8, 1, 0);
  strlen(v5, 160, "%s.Segment_Border_Y", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this + 12, 1, 0);
  strlen(v5, 160, "%s.Segment_Mask_X", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this + 16, 1, 0);
  strlen(v5, 160, "%s.Segment_Mask_Y", a3);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(5, v5, this + 20, 1, 0);
}

```

### `hudMapGlobal__SharedDataGlobalMap__FileIO_datParser__ref`
- **MC2 Xbox VA:** `0x0B5C80..0xb5d17` (160 B) | **MC3 Xbox VA:** `0x0BA2F0` (151 B, delta: `-9 B`) | **MC3 PS2 VA:** `0x288BD8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_2756f77eee7762c3fd1b490cf55ffeee24a0d2b636f7737cac492e49f6f287a6`

```cpp
int __thiscall hudMapGlobal__SharedDataGlobalMap__FileIO_datParser__ref(char *this, int a2)
{
  parFileIO__FileIO_datParser__ref(a2);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "StandardOpacity",
    this + 20,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "TriangleZoom",
    this + 24,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "PlayerTriangleZoom",
    this + 28,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "CircleZoom", this + 32, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "FlagZoom", this + 36, 1, 0);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
           9,
           "BackgoundColor",
           this + 40,
           1,
           0);
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

### `mcCarModEngine__FileIO_datParser__ref`
- **MC2 Xbox VA:** `0x0E9EC0..0xea0e1` (560 B) | **MC3 Xbox VA:** `0x129330` (233 B, delta: `-327 B`) | **MC3 PS2 VA:** `0x30CBD0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_d1f3dba934b211f9fe41ab3b0e752609537daf0568b8bad82c810e2865c40a00`

```cpp
int __thiscall mcCarModEngine__FileIO_datParser__ref(_DWORD *this, int a2)
{
  int v3; // eax
  int v4; // eax
  int v5; // eax

  vehChassisTune__Lerp_float_vehChassisTune_const__ptr__vehChassisTune_const__ptr(a2);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "SteeringLimit",
    this + 107,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "CenterOfMassY",
    this + 106,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "SSSValue", this + 94, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "SSSThreshold",
    this + 95,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "HillHorsepowerFactor",
    this + 86,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "CarFrictionHandlingWipeout",
    this + 87,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "AeroDampFactor",
    this + 90,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "LandingDampFactor",
    this + 89,
    1,
    0);
  if ( this[116] )
  {
    v3 = datParser__AddParser_char_const__ptr__datCallback__ptr("Nitro", 0);
    sub_E9170(v3);
  }
  if ( this[117] )
  {
    v4 = datParser__AddParser_char_const__ptr__datCallback__ptr("SSTurbo", 0);
    sub_EB430(v4);
  }
  if ( this[115] )
  {
    v5 = datParser__AddParser_char_const__ptr__datCallback__ptr("AIInfo", 0);
    sub_F2820(v5);
  }
  datParser__AddParser_char_const__ptr__datCallback__ptr("BurnOut", 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "Burnout_Threshold_Speed",
    this + 98,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "Burnout_Increase_Speed",
    this + 100,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "Burnout_Decrease_Speed",
    this + 101,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "Burnout_Boost_Speed",
    this + 103,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "Burnout_Damage_Amount",
    this + 102,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "Medium_Lod", this + 91, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "Low_Lod", this + 92, 1, 0);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
           6,
           "Very_Low_Lod",
           this + 93,
           1,
           0);
}

```

### `mcSpotlightTuneParams__FileIO_datParser__ref`
- **MC2 Xbox VA:** `0x121890..0x121979` (240 B) | **MC3 Xbox VA:** `0x03C0C0` (343 B, delta: `+103 B`) | **MC3 PS2 VA:** `0x1D6650`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_836a8e6b9aa627a0fae67f4d78c229b29da17c0a61b48e9dffca1c407369e192`

```cpp
int __thiscall mcSpotlightTuneParams__FileIO_datParser__ref(char *this, int a2)
{
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "falloff", this + 48, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "sharpness", this + 44, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "yscale", this + 32, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "m_hiBeamYScale",
    this + 36,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "m_aimTweak", this + 52, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "m_hiBeamTweak",
    this + 64,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "brightness", this + 28, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "colorr", this + 16, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "colorg", this + 20, 1, 0);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
           6,
           "colorb",
           this + 24,
           1,
           0);
}

```

### `lightGlowCondition__FileIO_datParser__ref`
- **MC2 Xbox VA:** `0x130AD0..0x130b93` (208 B) | **MC3 Xbox VA:** `0x093440` (195 B, delta: `-13 B`) | **MC3 PS2 VA:** `0x24CCE8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_38e6c50e9b813a10ab59c1b4771d74bfea28ad5b97dba7aa54cfde631a1ecc9a`

```cpp
int __thiscall lightGlowCondition__FileIO_datParser__ref(char *this, int a2)
{
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "softGlowScale",
    this + 44,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    9,
    "softGlowMultiply",
    this + 28,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "starScale", this + 80, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    9,
    "starMultiply",
    this + 64,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(6, "coneScale", this + 116, 1, 0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    9,
    "coneMultiply",
    this + 100,
    1,
    0);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
    6,
    "stripeScale",
    this + 152,
    1,
    0);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(
           9,
           "stripeMultiply",
           this + 136,
           1,
           0);
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

### `mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x1500D0..0x15035e` (656 B) | **MC3 Xbox VA:** `0x26F620` (219 B, delta: `-437 B`) | **MC3 PS2 VA:** `0x4B8DB0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_7d3831249372ca0bc0dddfc6507844f7e424b2e21aaec2a77146c66a92a8c727`

```cpp
int __thiscall mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref(_DWORD *this, int a2)
{
  _DWORD *v3; // eax
  int v4; // ecx
  int v5; // eax
  int v6; // ebp
  char *v7; // eax
  char *v8; // eax
  char *v9; // eax
  char *v10; // eax
  int v12; // [esp+1Ch] [ebp-8Ch] BYREF
  int v13; // [esp+20h] [ebp-88h] BYREF
  int v14; // [esp+24h] [ebp-84h] BYREF
  char v15[128]; // [esp+28h] [ebp-80h] BYREF

  this[1001] = 0;
  v3 = this + 1062;
  v4 = 60;
  do
  {
    *(v3 - 60) = 0;
    *v3 = 0;
    v3[60] = 0;
    ++v3;
    --v4;
  }
  while ( v4 );
  datBaseTokenizer__MatchIToken_char_const__ptr("movies");
  datBaseTokenizer__MatchToken_char_const__ptr("{");
  v5 = (*(int (__thiscall **)(int, const char *))(*(_DWORD *)a2 + 76))(a2, "nummovies");
  if ( v5 > 0 )
  {
    v6 = v5;
    do
    {
      (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
      if ( !strcasecmp("pre_city", v15) )
      {
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        v7 = (char *)_builtin_new(strlen(v15) + 1);
        this[1001] = v7;
        strcpy(v7, v15);
      }
      else if ( !strcasecmp("pre_race", v15) )
      {
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        sub_14FF90(v15, &v14);
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        v8 = (char *)_builtin_new(strlen(v15) + 1);
        this[v14 + 1002] = v8;
        strcpy(v8, v15);
      }
      else if ( !strcasecmp("post_race", v15) )
      {
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        sub_14FF90(v15, &v12);
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        v9 = (char *)_builtin_new(strlen(v15) + 1);
        this[v12 + 1062] = v9;
        strcpy(v9, v15);
      }
      else
      {
        if ( strcasecmp("alt_post_race", v15) )
          strcmp(
            "mcCityData::LoadMovieData: Unhandled token: %s, bailing out to avoid ambigous fatal error later on",
            v15);
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        sub_14FF90(v15, &v13);
        (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a2 + 4))(a2, v15, 128);
        v10 = (char *)_builtin_new(strlen(v15) + 1);
        this[v13 + 1122] = v10;
        strcpy(v10, v15);
      }
      --v6;
    }
    while ( v6 );
  }
  return datBaseTokenizer__MatchToken_char_const__ptr("}");
}

```

### `mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref`
- **MC2 Xbox VA:** `0x150AA0..0x150f94` (1280 B) | **MC3 Xbox VA:** `0x26F010` (736 B, delta: `-544 B`) | **MC3 PS2 VA:** `0x4B7C38`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_2a6dc37c637c319b92ece6151216a1b569decbfca70106a81099f388945f4077`

```cpp
int __userpurge mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref@<eax>(
        _DWORD *a1@<ecx>,
        const char *a2@<edi>,
        int a3,
        int a4,
        char a5)
{
  _DWORD *v5; // ebp
  int result; // eax
  _DWORD *v7; // esi
  bool v8; // al
  char *v9; // esi
  int v10; // eax
  _DWORD *v11; // esi
  char *v12; // eax
  int v13; // eax
  bool v14; // zf
  double v15; // st7
  float v16; // [esp+48h] [ebp-144h]
  char v18; // [esp+5Eh] [ebp-12Eh]
  char v19; // [esp+5Fh] [ebp-12Dh]
  int v20; // [esp+60h] [ebp-12Ch]
  _DWORD *v21; // [esp+64h] [ebp-128h]
  int v23; // [esp+6Ch] [ebp-120h]
  int v24; // [esp+70h] [ebp-11Ch]
  _DWORD *v25; // [esp+74h] [ebp-118h]
  char **v26; // [esp+78h] [ebp-114h]
  _DWORD *v27; // [esp+7Ch] [ebp-110h]
  char **v28; // [esp+80h] [ebp-10Ch]
  int v29; // [esp+84h] [ebp-108h]
  int v30; // [esp+88h] [ebp-104h]
  char v31[4]; // [esp+8Ch] [ebp-100h] BYREF
  char v32[124]; // [esp+90h] [ebp-FCh] BYREF
  _BYTE v33[128]; // [esp+10Ch] [ebp-80h] BYREF

  v5 = a1;
  a1[19] = 0;
  result = (*(int (__thiscall **)(int, const char *))(*(_DWORD *)a3 + 76))(a3, "numhookmen");
  v5[560] = result;
  v24 = 0;
  v29 = 0;
  LOWORD(v20) = 0;
  if ( result <= 0 )
  {
    v5[560] = 0;
  }
  else
  {
    v7 = v5 + 574;
    v23 = 590;
    v21 = v5 + 574;
    v27 = v5 + 561;
    do
    {
      datBaseTokenizer__MatchIToken_char_const__ptr("hookman");
      datBaseTokenizer__MatchToken_char_const__ptr("{");
      *(v7 - 2) = 0;
      *(v7 - 1) = 0;
      *v7 = -1;
      datBaseTokenizer__MatchIToken_char_const__ptr("name");
      (*(void (__thiscall **)(int, char *, int, const char *))(*(_DWORD *)a3 + 4))(a3, v31, 128, a2);
      HIBYTE(v20) = strcasecmp("arcade", v32) == 0;
      v8 = strcasecmp("battle_modes", v32) == 0;
      if ( HIBYTE(v20) || v8 )
      {
        BYTE2(v20) = 0;
      }
      else
      {
        BYTE2(v20) = 1;
        v9 = (char *)_builtin_new(strlen(v32) + 1);
        strcpy(v9, v32);
        *v28 = v9;
        v7 = a1;
      }
      a2 = "numraces";
      v10 = (*(int (__thiscall **)(int))(*(_DWORD *)a3 + 76))(a3);
      v5[19] += v10;
      v28 = 0;
      if ( v10 > 0 )
      {
        v25 = v5 + 953;
        v11 = &v5[8 * v20 + 80];
        v26 = (char **)&v5[v20 + 20];
        v30 = v10;
        do
        {
          (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a3 + 4))(a3, v31, 128);
          *v11 = mc__LookupRaceType_char_const__ptr(v31);
          (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a3 + 4))(a3, v31, 128);
          v12 = (char *)_builtin_new(strlen(v31) + 1);
          strcpy(v12, v31);
          *v26 = v12;
          v13 = *v11;
          v14 = *v11 == 2;
          *((_BYTE *)v11 + 13) = 0;
          *((_BYTE *)v11 + 14) = 1;
          v11[1] = 1008981770;
          v11[2] = 1036831949;
          *((_BYTE *)v11 + 12) = 0;
          *((_BYTE *)v11 + 15) = 0;
          if ( v14 )
          {
            if ( v18 )
              *v21 = v20;
          }
          else if ( v13 == 3 )
          {
            (*(void (__thiscall **)(int, char *, int))(*(_DWORD *)a3 + 4))(a3, v31, 128);
            if ( v18 )
              a1[v23 + mc__mcCityData__LookupHookmanRace_char_const__ptr__int(a1, v24, v31)] = v20;
          }
          else if ( v18 )
          {
            a1[(_DWORD)v28 + v23 - 15] = v20;
            a1[(_DWORD)v28 + v23] = -1;
            ++*(v21 - 1);
            v28 = (char **)((char *)v28 + 1);
          }
          else if ( v19 )
          {
            *(v25 - 15) = v20;
            *v25 = -1;
            ++a1[936];
          }
          else
          {
            v25[18] = v20;
            v25[33] = -1;
            ++a1[969];
          }
          if ( a5 && *v11 != 3 )
          {
            (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
            datBaseTokenizer__MatchToken_char_const__ptr("{");
            (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
            *((_BYTE *)v11 + 14) = mc__LookupTOD_char_const__ptr(v33);
            (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
            *((_BYTE *)v11 + 13) = mc__LookupWeather_char_const__ptr(v33);
            (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
            if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("AmbientDensity:", 0) )
            {
              (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
              v15 = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a4 + 20))(a4);
              v16 = v15;
              sub_1507E0(v16);
              *((float *)v11 + 1) = v15;
              (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
              *((float *)v11 + 2) = ((double (__thiscall *)(int))*(_DWORD *)(*(_DWORD *)a4 + 20))(a4);
            }
            if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("ForcedVehicle:", 1) )
            {
              (*(void (__thiscall **)(int, _BYTE *, int))(*(_DWORD *)a4 + 4))(a4, v33, 128);
              v11[7] = mc__LookupCar_char_const__ptr(v33);
            }
            else
            {
              v11[7] = 33;
            }
            datBaseTokenizer__MatchToken_char_const__ptr("}");
          }
          ++v20;
          v11 += 8;
          v14 = v30 == 1;
          ++v26;
          ++v25;
          --v30;
        }
        while ( !v14 );
        v5 = a1;
        v7 = v21;
      }
      if ( v18 )
      {
        ++v24;
        v7 += 33;
        ++v27;
        v21 = v7;
        v23 += 33;
      }
      datBaseTokenizer__MatchToken_char_const__ptr("}");
      ++v29;
    }
    while ( v29 < v5[560] );
    result = v24;
    v5[560] = v24;
  }
  return result;
}

```

### `mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool`
- **MC2 Xbox VA:** `0x151000..0x151097` (160 B) | **MC3 Xbox VA:** `N/A` (0 B, delta: `+0 B`) | **MC3 PS2 VA:** `0x4B7900`
- **Match Method:** `ps2_callgraph` | **REA Function Evidence ID:** `ev_30fe4233a67a466cb5485d8facdc340d1838bba58d238c9481fd2d793284ab8e`

```cpp
int __cdecl mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool(const char *a1, int a2, char a3)
{
  int result; // eax
  char v4; // bl
  char **v5; // esi
  char **v6; // ebp
  _BYTE v7[128]; // [esp+10h] [ebp-80h] BYREF

  datBaseTokenizer__MatchIToken_char_const__ptr("city");
  result = (*(int (__thiscall **)(const char *, _BYTE *, int))(*(_DWORD *)a1 + 4))(a1, v7, 128);
  v4 = 0;
  v5 = off_34F4F8;
  v6 = off_34F2E4;
  do
  {
    if ( v4 )
      break;
    result = strcasecmp(v7, *v6);
    if ( !result )
    {
      mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref(v5, a1, (int)a1, a2, a3);
      result = mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref(v5, (int)a1);
      v4 = 1;
    }
    ++v6;
    v5 += 1182;
  }
  while ( (int)v6 < (int)&dword_34F2F4 );
  return result;
}

```

### `mcUnlocking__IsSlipstreamTurboUnlocked_bool_const`
- **MC2 Xbox VA:** `0x1532C0..0x153310` (80 B) | **MC3 Xbox VA:** `0x289D80` (80 B, delta: `+0 B`) | **MC3 PS2 VA:** `0x4D4750`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_90cba3cf2ca4dad9371af3ab530e123f94d5ecbefbc534080f5f587272d69001`

```cpp
char __thiscall mcUnlocking__IsSlipstreamTurboUnlocked_bool_const(int *this, char a2)
{
  if ( byte_3AC6E9 == 1 )
    return 1;
  if ( a2 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 4, 0);
  return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 4, 0)
      || mcUnlocking__EvaluateUnlockRule_int_int_const(this, 8, 0);
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

### `sndBank__AddStream_char_const__ptr__bool_bool`
- **MC2 Xbox VA:** `0x1D4BF0..0x1d4d37` (336 B) | **MC3 Xbox VA:** `0x218220` (425 B, delta: `+89 B`) | **MC3 PS2 VA:** `0x4489F0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_8be42b3eaa6b26c792f4d8b988959ceafec4b19c919c64e8ec20ccccf531bb8f`

```cpp
int __thiscall sndBank__AddStream_char_const__ptr__bool_bool(void *this, const char *a2, char a3)
{
  int v3; // eax
  int v4; // esi
  int v5; // ebp
  _WORD *v6; // edi
  char v7; // al
  unsigned int v8; // eax
  char *v9; // edi
  const char *v11; // edx
  int v13; // [esp+Ch] [ebp-114h] BYREF
  __int16 v14; // [esp+10h] [ebp-110h]
  __int16 v15; // [esp+12h] [ebp-10Eh]
  void *v16; // [esp+14h] [ebp-10Ch]
  int v17; // [esp+18h] [ebp-108h] BYREF
  char v18[260]; // [esp+1Ch] [ebp-104h] BYREF

  v16 = this;
  v3 = _builtin_new(24);
  v4 = v3;
  if ( v3 )
  {
    mcControlConfigMgr__mcControlConfigMgr_void(v3);
    *(_DWORD *)v4 = &off_33D5BC;
    *(_DWORD *)(v4 + 12) = 0;
    *(_WORD *)(v4 + 16) = 0;
    *(_WORD *)(v4 + 18) = 0;
    *(_BYTE *)(v4 + 20) = 1;
    v5 = v4;
  }
  else
  {
    v5 = 0;
  }
  strcpy(v18, "Stream");
  v6 = (_WORD *)((char *)&v17 + 3);
  do
  {
    v7 = *((_BYTE *)v6 + 1);
    v6 = (_WORD *)((char *)v6 + 1);
  }
  while ( v7 );
  *v6 = 58;
  v8 = strlen(a2) + 1;
  v9 = (char *)&v17 + 3;
  while ( *++v9 )
    ;
  qmemcpy(v9, a2, v8);
  sub_1D44C0(v18);
  *(_WORD *)(v5 + 16) = 0;
  sub_1FB7C0(a2, strlen(v11));
  *(_BYTE *)(v5 + 20) = a3;
  v17 = v5;
  v13 = 0;
  v14 = 0;
  v15 = 0;
  sub_1FB7C0(v18, strlen(v18));
  sub_1D48D0(&v13, &v17);
  return _builtin_delete(v13);
}

```

### `crSkeletonData__Load_Stream__ptr__char_const__ptr`
- **MC2 Xbox VA:** `0x1DEA50..0x1deba2` (352 B) | **MC3 Xbox VA:** `0x3530B0` (503 B, delta: `+151 B`) | **MC3 PS2 VA:** `0x58DC18`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_6977ef918bb0ef58b18f04a5475fff231433907b058fe852f5d13c08c81fe653`

```cpp
char __thiscall crSkeletonData__Load_Stream__ptr__char_const__ptr(unsigned __int8 *this, int a2, int a3)
{
  int v5; // edi
  int v6; // eax
  int v7; // esi
  int v8; // ecx
  int v9; // eax
  char v10; // bl
  bool v11; // zf
  bool v12; // cc
  char v13; // al
  int v14; // [esp+8h] [ebp-1ACh] BYREF
  int Int_void; // [esp+Ch] [ebp-1A8h]
  int v16; // [esp+10h] [ebp-1A4h] BYREF
  _BYTE v17[160]; // [esp+14h] [ebp-1A0h] BYREF
  _BYTE v18[256]; // [esp+B4h] [ebp-100h] BYREF

  datTokenizer__datTokenizer_char_const__ptr__Stream__ptr(a3, a2);
  if ( (unsigned __int8)datBaseTokenizer__CheckIToken_char_const__ptr__bool("version:", 1) )
    Int_void = datAsciiTokenizer__GetInt_void(v17);
  else
    Int_void = 100;
  datBaseTokenizer__MatchToken_char_const__ptr("NumBones");
  *this = datAsciiTokenizer__GetInt_void(v17);
  datBaseTokenizer__GetToken_char__ptr__int(v18, 256);
  if ( strncmp(v18, "bone", 4) )
  {
    Stream__Close_void(a2);
    return 0;
  }
  v5 = *this;
  v6 = _builtin_new(140 * v5);
  v7 = v6;
  if ( v6 )
  {
    swfVARIANT__asInt_void_const(v6, 140, v5, sub_1DED40);
    v8 = v7;
  }
  else
  {
    v8 = 0;
  }
  v9 = Int_void;
  v10 = 0;
  v11 = Int_void == 100;
  v12 = Int_void <= 100;
  *((_DWORD *)this + 2) = v8;
  v14 = v8 + 140;
  v16 = 0;
  if ( v11 )
  {
    v13 = crBoneData__Load_v100_datTokenizer__ref__crBoneData__ptr__ptr__int__ref(v17, &v14, &v16);
  }
  else
  {
    if ( v12 || v9 > 103 )
      return v10;
    v13 = crBoneData__Load_v101_datTokenizer__ref__crBoneData__ptr__ptr__int__ref(v17, &v14, &v16);
  }
  v10 = v13;
  if ( v13 )
  {
    sub_1DE890(this);
    sub_1DE800(this);
  }
  return v10;
}

```

### `txtStringTable__Load_char_const__ptr__txtLanguage__eLanguage_unsigned_int_bool_bool`
- **MC2 Xbox VA:** `0x1E1170..0x1e13c1` (608 B) | **MC3 Xbox VA:** `0x0EA480` (655 B, delta: `+47 B`) | **MC3 PS2 VA:** `0x2BE210`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_035ad0029cab4bd599c98c12ed21fe44546252115f9c6dbec7d11726accc0831`

```cpp
char __thiscall txtStringTable__Load_char_const__ptr__txtLanguage__eLanguage_unsigned_int_bool_bool(
        _DWORD *this,
        int a2,
        int a3,
        int a4,
        char a5)
{
  int v6; // esi
  int v7; // eax
  int v8; // eax
  int Stream__ptr; // ebp
  int v11; // edi
  int v12; // eax
  _DWORD *v13; // eax
  int i; // [esp+Ch] [ebp-12Ch]
  int j; // [esp+Ch] [ebp-12Ch]
  int v16; // [esp+10h] [ebp-128h] BYREF
  int v17; // [esp+14h] [ebp-124h] BYREF
  int v18; // [esp+18h] [ebp-120h] BYREF
  _BYTE v19[4]; // [esp+1Ch] [ebp-11Ch] BYREF
  _DWORD v20[6]; // [esp+20h] [ebp-118h] BYREF
  _BYTE v21[256]; // [esp+38h] [ebp-100h] BYREF

  v6 = 0;
  if ( _builtin_new(12) )
    v7 = txtHashTable__txtHashTable_int(100);
  else
    v7 = 0;
  *this = v7;
  v8 = sub_20BD60(a2, 1);
  if ( !v8 )
  {
    sub_20A980(v21, 256, "fonts", a2, "strtbl");
    v8 = sub_20BD60(v21, 1);
    if ( !v8 )
      return 0;
  }
  Stream__ptr = Stream__PreLoad_Stream__ptr(v8);
  v18 = 0;
  Stream__Read_void__ptr__int(&v18, 4);
  v11 = 0;
  for ( i = 0; v11 < v18; ++v11 )
  {
    Stream__Read_void__ptr__int(&v16, 4);
    if ( v11 == a3 )
      i = v16;
  }
  Stream__Read_void__ptr__int(v19, 4);
  if ( a5 )
  {
    Stream__Read_void__ptr__int(this + 2, 4);
    this[1] = _builtin_new(4 * this[2]);
    if ( (int)this[2] > 0 )
    {
      do
      {
        Stream__Read_void__ptr__int(&v16, 4);
        *(_DWORD *)(this[1] + 4 * v6) = _builtin_new(v16 + 1);
        Stream__Read_void__ptr__int(*(_DWORD *)(this[1] + 4 * v6), v16 + 1);
        *(_BYTE *)(v16 + *(_DWORD *)(this[1] + 4 * v6++)) = 0;
      }
      while ( v6 < this[2] );
    }
  }
  if ( i )
  {
    Stream__Seek_int(i);
    v17 = 0;
    Stream__Read_void__ptr__int(&v17, 4);
    for ( j = 0; j < v17; ++j )
    {
      txtStringData__txtStringData_void(v20);
      if ( (unsigned __int8)txtStringData__Load_Stream__ptr__unsigned_int(Stream__ptr, a4) )
      {
        v12 = _builtin_new(24);
        if ( v12 )
          v13 = (_DWORD *)txtStringData__txtStringData_void(v12);
        else
          v13 = 0;
        qmemcpy(v13, v20, 0x18u);
        sub_1E22C0(*v13, v13);
      }
      v20[1] = 0;
      v20[2] = 0;
      txtStringData__dtor_txtStringData_void(v20);
    }
    Stream__Close_void(Stream__ptr);
    if ( v17 )
    {
      return 1;
    }
    else
    {
      sub_1E1720(a3);
      return 0;
    }
  }
  else
  {
    Stream__Close_void(Stream__ptr);
    return 0;
  }
}

```

### `txtStringTable__Get_char_const__ptr`
- **MC2 Xbox VA:** `0x1E1410..0x1e15bb` (432 B) | **MC3 Xbox VA:** `0x0EA750` (461 B, delta: `+29 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_452df3c91f9539f67daa9e2303eeb2dcc783c925776af61657bfbc4167b13963`

```cpp
_DWORD *__thiscall txtStringTable__Get_char_const__ptr(_DWORD *this, const char *a2)
{
  bool v2; // zf
  const char *v4; // edi
  int v5; // eax
  _DWORD *v6; // esi
  unsigned int v7; // eax
  char *v8; // edi
  char *v10; // edi
  int v12; // esi
  int v13; // eax
  int v14; // ebx
  unsigned int v15; // esi
  int v16; // eax
  char v17; // [esp-1h] [ebp-11h] BYREF
  char v18[12]; // [esp+0h] [ebp-10h] BYREF
  _DWORD *v19; // [esp+Ch] [ebp-4h]

  v2 = *this == 0;
  v19 = this;
  if ( v2 )
    return 0;
  v4 = a2;
  v5 = sub_1E13D0(a2);
  v6 = (_DWORD *)sub_1E2340(v5);
  if ( !v6 )
  {
    if ( dword_354790 != 1 )
    {
      if ( dword_354790 == 2 )
        goto LABEL_9;
      if ( dword_354790 == 3 )
        strcmp("String '%s' not in stringtable", a2);
    }
    if ( dword_354790 != 2 )
    {
      if ( !a2 )
      {
        v14 = 0;
LABEL_18:
        v16 = _builtin_new(24);
        if ( v16 )
          v6 = (_DWORD *)txtStringData__txtStringData_void(v16);
        else
          v6 = 0;
        v6[2] = TStringDuplicate_unsigned_wchar_t_const__ptr(v14);
        *v6 = sub_1E13D0(v4);
        v6[1] = txtGetFontTex_char_const__ptr__bool(dword_540394, 0);
        sub_1E22C0(*v6, v6);
        return v6;
      }
      v15 = strlen(a2) + 1;
      mcControlConfigMap__ClearAllMaps_void(v18[0]);
      v13 = sub_1AEC0(v18, a2, v15);
LABEL_17:
      v14 = v13;
      goto LABEL_18;
    }
LABEL_9:
    strlen(a2);
    mcControlConfigMap__ClearAllMaps_void(v18[0]);
    strcpy(v18, "!!");
    v7 = strlen(a2) + 1;
    v8 = &v17;
    while ( *++v8 )
      ;
    qmemcpy(v8, a2, v7);
    v10 = &v17;
    while ( *++v10 )
      ;
    strcpy(v10, "!!");
    v12 = &v18[strlen(v18) + 1] - v18;
    mcControlConfigMap__ClearAllMaps_void(v18[0]);
    v13 = sub_1AEC0(v18, v18, v12);
    v4 = a2;
    goto LABEL_17;
  }
  return v6;
}

```

### `txtFontTex__SetBilinear_bool`
- **MC2 Xbox VA:** `0x1F17A0..0x1f17b0` (16 B) | **MC3 Xbox VA:** `0x0EBC90` (74 B, delta: `+58 B`) | **MC3 PS2 VA:** `0x2BDB70`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_923134181cc6d4439a04931e7b78ddd7eab7cbdcdc61483ce962b821b7cde168`

```cpp
char *__cdecl txtFontTex__SetBilinear_bool(char *a1)
{
  char *result; // eax

  result = off_354DC4;
  off_354DC4 = a1;
  return result;
}

```

### `datAssetManager__SetPath_char_const__ptr`
- **MC2 Xbox VA:** `0x20A720..0x20a736` (32 B) | **MC3 Xbox VA:** `0x20D190` (22 B, delta: `-10 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `insn_signature` | **REA Function Evidence ID:** `ev_512cc932e3a79c7e10b98aa520bc07d39526b88536c2c18793b4993caedf56f6`

```cpp
int __cdecl datAssetManager__SetPath_char_const__ptr(int a1)
{
  return sub_20A6D0(a1);
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

### `datAssetManager__Open_char_const__ptr__char_const__ptr__bool_bool`
- **MC2 Xbox VA:** `0x20AA60..0x20aa95` (64 B) | **MC3 Xbox VA:** `0x20D6F0` (266 B, delta: `+202 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `prop_round_3` | **REA Function Evidence ID:** `ev_48074c5fd8168b8bfafb3a9223e4c53199e0341841458c0024c990538d22b358`

```cpp
int __thiscall datAssetManager__Open_char_const__ptr__char_const__ptr__bool_bool(void *this, int a2, int a3, int a4)
{
  _BYTE v5[256]; // [esp+10h] [ebp-100h] BYREF

  (*(void (__thiscall **)(void *, _BYTE *, int, int, int))(*(_DWORD *)this + 4))(this, v5, 256, a2, a3);
  return sub_20BDF0(v5);
}

```

## 2. Full Symbol Equivalence Table (276 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x011130` | `0x012440` | `-` | `Main_void` | 509 | 553 | +44 | `seed` |
| `0x017C20` | `0x01DB60` | `0x1A4030` | `mcLoadScreenTransition__FileIO_datParser__ref` | 128 | 81 | -47 | `seed` |
| `0x0220E0` | `0x059150` | `0x55F490` | `parFileIO__FileIO_datParser__ref` | 16 | 3 | -13 | `seed` |
| `0x040AC4` | `0x15B640` | `0x37C090` | `mcChatListMenu__FileIO_datParser__ref` | 124 | 177 | +53 | `seed` |
| `0x041E78` | `0x15BE30` | `0x379F98` | `mcNetworkWaiting__FileIO_datParser__ref` | 1032 | 3158 | +2126 | `seed` |
| `0x0477F9` | `0x165ED0` | `0x34BAA0` | `GetTrafficDenString_int` | 820 | 69 | -751 | `seed` |
| `0x047B2D` | `0x165E50` | `0x34B9D0` | `mcMenuCustom__GetTODString_int` | 298 | 42 | -256 | `seed` |
| `0x047C57` | `0x1851F0` | `0x34D408` | `mcMenuCustomRaceType__GetTeamModeString_int` | 2607 | 69 | -2538 | `seed` |
| `0x04D9B0` | `0x33D600` | `0x578538` | `mcFeMemCard__FileIO_datParser__ref` | 144 | 106 | -38 | `seed` |
| `0x0620F0` | `0x169060` | `0x366300` | `mcMenuMsgBox__FileIO_datParser__ref` | 80 | 38 | -42 | `seed` |
| `0x0634B0` | `0x192D30` | `0x381568` | `TextAnimConfig__FileIO_datParser__ref__char_const__ptr` | 112 | 111 | -1 | `seed` |
| `0x0689D0` | `0x350970` | `-` | `mcUiHeading__FileIO_datParser__ref` | 48 | 48 | +0 | `prop_round_2` |
| `0x069000` | `0x350A70` | `0x582030` | `mcUiHeading__FileIO_datParser__ref` | 379 | 858 | +479 | `seed` |
| `0x07C0D0` | `0x349370` | `0x58ADA0` | `mcUiListMenu__columnData__FileIO_char_const__ptr__datParser__ref` | 848 | 1026 | +178 | `seed` |
| `0x07C420` | `0x349780` | `0x58B268` | `mcUiListMenu__columnData__FileIO_char_const__ptr__datParser__ref` | 160 | 200 | +40 | `seed` |
| `0x0808E0` | `0x2C9840` | `0x50F788` | `mcPlayerInputTune__FileIO_datParser__ref` | 128 | 255 | +127 | `seed` |
| `0x084D20` | `0x2CE170` | `0x520A28` | `mcCinematicType__FileIO_datParser__ptr` | 112 | 321 | +209 | `seed` |
| `0x084E46` | `0x2CE650` | `0x5216B0` | `mcCinematicCS__FileIO_datParser__ref` | 522 | 357 | -165 | `seed` |
| `0x086110` | `0x2CF970` | `0x51CA48` | `mcTrackCS__FileIO_datParser__ref` | 1264 | 1210 | -54 | `seed` |
| `0x0867F0` | `0x2D01C0` | `0x51B180` | `mcPovCS__FileIO_datParser__ref` | 80 | 96 | +16 | `seed` |
| `0x08CC50` | `0x0CBA90` | `-` | `BackDrop__LoadLink_BackdropItem__ptr__datAsciiTokenizer__ref` | 1360 | 277 | -1083 | `seed` |
| `0x091F90` | `0x0EEDF0` | `0x2BF3A8` | `mcArchetypeBreak__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 160 | 199 | +39 | `seed` |
| `0x09BF90` | `0x1CA900` | `-` | `mcRaceBase__LoadWeather_datAsciiTokenizer__ref` | 384 | 228 | -156 | `seed` |
| `0x09C3F0` | `0x1CAEF0` | `0x3D7960` | `mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref` | 336 | 331 | -5 | `seed` |
| `0x09C540` | `0x1CB040` | `0x3D7B80` | `mcRaceBase__LoadOpponentPersonality_int_datAsciiTokenizer__ref` | 512 | 523 | +11 | `seed` |
| `0x09C830` | `0x1CB380` | `0x3D8820` | `mcRaceBase__LoadAmbientRoadOverride_datAsciiTokenizer__ref` | 336 | 334 | -2 | `seed` |
| `0x09C980` | `0x1CB4D0` | `0x3D89F0` | `mcRaceBase__LoadClosedRoads_datAsciiTokenizer__ref` | 144 | 126 | -18 | `seed` |
| `0x09CA10` | `0x1D1440` | `0x3D8F30` | `mcRaceBase__LoadPreRaceCam_datAsciiTokenizer__ref` | 256 | 204 | -52 | `seed` |
| `0x09E5E0` | `0x1D2150` | `0x3D1840` | `aiRaceShortcut__LoadShortcut_datAsciiTokenizer__ref` | 304 | 335 | +31 | `seed` |
| `0x09E9A0` | `0x1CDC80` | `-` | `mcRaceBase__LoadCheckpoints_datAsciiTokenizer__ref` | 800 | 667 | -133 | `seed` |
| `0x09ECC0` | `0x1D4CA0` | `0x3D7F88` | `mcRaceBase__LoadPathFindingShortcuts_datAsciiTokenizer__ref` | 144 | 123 | -21 | `seed` |
| `0x0A13F0` | `0x1D28C0` | `0x3D1288` | `aiOpponentStart__LoadPreRacePath_datAsciiTokenizer__ref` | 64 | 103 | +39 | `seed` |
| `0x0A1840` | `0x20F560` | `-` | `datBaseTokenizer__SkipToEndOfLine_void` | 112 | 72 | -40 | `prop_round_2` |
| `0x0A26A0` | `0x1D3AE0` | `0x3D6ED8` | `mcRaceBase__LoadOpponents_datAsciiTokenizer__ref` | 1552 | 2116 | +564 | `seed` |
| `0x0A34F0` | `0x1D4F20` | `0x3D4A20` | `mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref` | 475 | 2832 | +2357 | `career_semantic_seed` |
| `0x0A379D` | `0x1D4F20` | `0x3D4A20` | `mcRaceBase__Load_datAsciiTokenizer__ref__mcRaceBase__ptr` | 1539 | 2818 | +1279 | `seed` |
| `0x0AC160` | `0x1C8380` | `0x3CDC58` | `mcCheckpointTuneParams__FileIO_datParser__ref` | 16 | 502 | +486 | `seed` |
| `0x0AC1B0` | `0x1C85D0` | `0x3CDC78` | `mcCheckpointTuneParams__FileIO_datParser__ref` | 320 | 333 | +13 | `seed` |
| `0x0B0010` | `0x1D5AE0` | `0x3D0510` | `mcRaceAmbient__Load_datAsciiTokenizer__ref` | 32 | 23 | -9 | `seed` |
| `0x0B0030` | `0x1D5B00` | `0x3D0F88` | `mcRaceAmbient__FindMotionPathType_datAsciiTokenizer__ref` | 80 | 79 | -1 | `seed` |
| `0x0B0170` | `0x1D5B70` | `0x3D0708` | `mcRaceAmbient__LoadProperties_datAsciiTokenizer__ref` | 160 | 148 | -12 | `seed` |
| `0x0B0440` | `0x1D5F10` | `0x3D08B8` | `mcRaceAmbient__LoadPathNodes_datAsciiTokenizer__ref` | 416 | 423 | +7 | `seed` |
| `0x0B05E0` | `0x1D60C0` | `0x3D0540` | `mcRaceAmbient__Load_datAsciiTokenizer__ref__char_const__ptr__char_const__ptr` | 77 | 316 | +239 | `prop_round_1` |
| `0x0B0850` | `0x227B90` | `0x465FC0` | `mcCreatureManager__LoadRaceStarterData_datAsciiTokenizer__ref__mcCreatureAnimMgr__ref__bool` | 1008 | 504 | -504 | `seed` |
| `0x0B5820` | `0x0BA0D0` | `0x287DB0` | `hudMapLocal__SharedDataLocalMap__TextureData__FileIO_datParser__ref__char_const__ptr` | 320 | 310 | -10 | `seed` |
| `0x0B5C80` | `0x0BA2F0` | `0x288BD8` | `hudMapGlobal__SharedDataGlobalMap__FileIO_datParser__ref` | 160 | 151 | -9 | `seed` |
| `0x0B617F` | `0x0BC800` | `0x2855E0` | `hudMap__SharedDataAllTypes__FileIO_datParser__ref` | 261 | 143 | -118 | `seed` |
| `0x0B64D0` | `0x0BD150` | `0x287AA0` | `hudMapLocal__SharedDataLocalMap__FileIO_datParser__ref` | 512 | 507 | -5 | `seed` |
| `0x0B89A0` | `0x0B3590` | `0x297170` | `hudSplashBase__FileIO_datParser__ref` | 48 | 33 | -15 | `prop_round_2` |
| `0x0B8C00` | `0x0B3750` | `0x297658` | `hudSplashText__FileIO_datParser__ref` | 48 | 126 | +78 | `seed` |
| `0x0B8E10` | `0x0B3A60` | `0x297B78` | `hudSplashToTimerAnim__FileIO_datParser__ref__char_const__ptr` | 176 | 172 | -4 | `seed` |
| `0x0B90D0` | `0x0B3D60` | `0x297FE8` | `hudSplashSimpleZoomInAnim__FileIO_datParser__ref__char_const__ptr` | 336 | 327 | -9 | `seed` |
| `0x0B9490` | `0x0B4289` | `0x2986A8` | `hudSplashToTimerAnim__FileIO_datParser__ref__char_const__ptr` | 384 | 500 | +116 | `seed` |
| `0x0BA290` | `0x0DC1F0` | `0x279460` | `hudElement__FileIO_datParser__ref` | 64 | 63 | -1 | `seed` |
| `0x0BA8D0` | `0x0DC8B0` | `0x274218` | `hudChatBox__SharedData__FileIO_datParser__ref` | 208 | 195 | -13 | `seed` |
| `0x0BB2D0` | `0x0D2230` | `0x279B78` | `hudFlag__SharedData__FileIO_datParser__ref` | 128 | 91 | -37 | `seed` |
| `0x0BB5F0` | `0x0D25D0` | `0x28C038` | `hudPowerup__FileIO_datParser__ref` | 96 | 85 | -11 | `seed` |
| `0x0BBF40` | `0x0D7970` | `-` | `hudLapCounter__FileIO_datParser__ref` | 64 | 50 | -14 | `prop_round_1` |
| `0x0BBFD0` | `0x0D7A10` | `0x27CB40` | `hudLapCounter__FileIO_datParser__ref` | 64 | 69 | +5 | `seed` |
| `0x0BD320` | `0x0D98F0` | `0x5BCC30` | `mcHudTimer__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 143 | +127 | `seed` |
| `0x0BD330` | `0x0D9990` | `0x28E9D8` | `mcHudTimer__SharedData__FileIO_datParser__ref` | 176 | 151 | -25 | `seed` |
| `0x0BD400` | `0x0D9A30` | `0x5BCC40` | `mcHudTimer__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BD500` | `0x0D9AE0` | `0x5BCC50` | `mcHudTimer__GetTypeName_void` | 16 | 184 | +168 | `seed` |
| `0x0BE780` | `0x0B7D30` | `-` | `mcRaceBase__FileIO_datParser__ref` | 48 | 5 | -43 | `prop_round_2` |
| `0x0BE8E0` | `0x0D5400` | `0x28CF50` | `hudSSTurbo__SharedData__FileIO_datParser__ref` | 192 | 135 | -57 | `seed` |
| `0x0BEF40` | `0x0D59B0` | `0x275EF0` | `hudDamage__SharedData__TextureData__FileIO_datParser__ref__char_const__ptr` | 320 | 310 | -10 | `seed` |
| `0x0BF410` | `0x0D5EB0` | `-` | `hudDamage__SharedData__FileIO_datParser__ref` | 160 | 199 | +39 | `seed` |
| `0x0BF4C0` | `0x0D5F80` | `0x275DE0` | `hudDamage__SharedData__FileIO_datParser__ref` | 224 | 143 | -81 | `seed` |
| `0x0C04C0` | `0x0D41B0` | `-` | `hudTachometer__SharedData__FileIO_datParser__ref` | 128 | 196 | +68 | `seed` |
| `0x0C0540` | `0x0D4280` | `0x2997E0` | `hudTachometer__SharedData__FileIO_datParser__ref` | 128 | 143 | +15 | `seed` |
| `0x0C13F0` | `0x0DBA30` | `0x293E40` | `hudRearViewMirror__SharedData__FileIO_datParser__ref` | 224 | 223 | -1 | `seed` |
| `0x0C19A0` | `0x0D1370` | `0x29CB60` | `hudArrow__FileIO_datParser__ref` | 224 | 210 | -14 | `seed` |
| `0x0C5260` | `0x1E6360` | `0x4080A0` | `aiPathGraph__Load_datAsciiTokenizer__ref__mcRaceBase__ptr` | 1072 | 650 | -422 | `seed` |
| `0x0C5720` | `0x1E6CB0` | `0x3FE820` | `mcHeliRace__Load_datAsciiTokenizer__ref` | 32 | 23 | -9 | `seed` |
| `0x0C5740` | `0x1E6C20` | `0x3FE848` | `mcHeliRace__LoadProperties_datAsciiTokenizer__ref` | 144 | 129 | -15 | `seed` |
| `0x0C7E90` | `0x1ED090` | `0x404988` | `aiOpponent__FileIO_datParser__ref` | 16 | 396 | +380 | `seed` |
| `0x0C7EB0` | `0x1ED240` | `0x4049A8` | `aiOpponent__FileIO_datParser__ref` | 160 | 147 | -13 | `seed` |
| `0x0E8410` | `0x10A820` | `0x2F0F28` | `opponentTuneStaticData__FileIO_datParser__ref` | 256 | 242 | -14 | `seed` |
| `0x0E9EC0` | `0x129330` | `0x30CBD0` | `mcCarModEngine__FileIO_datParser__ref` | 560 | 233 | -327 | `seed` |
| `0x0EC070` | `0x33CC00` | `0x56F1A0` | `vehEngineSoundData__FileIO_datParser__ref` | 240 | 288 | +48 | `seed` |
| `0x0ECC00` | `0x33BFC0` | `0x570D70` | `vehWheelSoundData__FileIO_datParser__ref` | 352 | 691 | +339 | `seed` |
| `0x0ED3C0` | `0x33D2A0` | `0x5713D0` | `vehWindNoiseSoundData__FileIO_datParser__ref` | 112 | 113 | +1 | `seed` |
| `0x0ED9B0` | `0x14EF90` | `0x324448` | `mcGarage__InitStringArray_void` | 464 | 4208 | +3744 | `seed` |
| `0x0F2E60` | `0x12A130` | `0x30EB80` | `mcCarStuckTune__FileIO_datParser__ref` | 48 | 499 | +451 | `seed` |
| `0x0F5B80` | `0x124B70` | `0x2D85F0` | `mcGyroTune__FileIO_datParser__ref` | 656 | 1054 | +398 | `seed` |
| `0x0F6990` | `0x10E470` | `0x2F2C08` | `mcPowerUpType__FileIO_datParser__ref` | 160 | 304 | +144 | `seed` |
| `0x0F96D0` | `0x0CBDB0` | `0x2A2DC8` | `BackDrop__LoadBorderCurved_BackdropItem__ptr__datAsciiTokenizer__ref` | 1600 | 732 | -868 | `seed` |
| `0x0FC420` | `0x12EEB0` | `0x30C338` | `mcCarAeroTune__FileIO_datParser__ref` | 160 | 145 | -15 | `seed` |
| `0x0FC610` | `0x12EBE0` | `0x30C8E8` | `mcCarFluidTune__FileIO_datParser__ref` | 144 | 123 | -21 | `seed` |
| `0x0FC950` | `0x069ED0` | `-` | `aiAmbientTrafficData__FileIO_datParser__ref` | 80 | 71 | -9 | `insn_signature` |
| `0x0FCB00` | `0x069FA0` | `0x21AEE8` | `aiAmbientTrafficData__FileIO_datParser__ref` | 128 | 63 | -65 | `seed` |
| `0x10A89F` | `0x07C736` | `0x221C10` | `aiAmbientType__FileIO_datParser__ref` | 801 | 670 | -131 | `seed` |
| `0x10C780` | `0x07FD10` | `0x230D70` | `InitializeTokenizer_datAsciiTokenizer__ref__char_const__ptr__char_const__ptr` | 144 | 144 | +0 | `seed` |
| `0x10C810` | `0x07FDA0` | `0x231428` | `mcAmbientDistrib__LoadHeader_datAsciiTokenizer__ref` | 208 | 211 | +3 | `seed` |
| `0x10EDF0` | `0x0827B8` | `0x2328C8` | `mcTrainBuilder__LoadTrainSegments_mcTrain__ref__datBaseTokenizer__ref` | 304 | 424 | +120 | `seed` |
| `0x112CD0` | `0x2B99A0` | `0x503448` | `aiRailNetwork__LoadOverridenRoad_datAsciiTokenizer__ref` | 217 | 213 | -4 | `seed` |
| `0x121890` | `0x03C0C0` | `0x1D6650` | `mcSpotlightTuneParams__FileIO_datParser__ref` | 240 | 343 | +103 | `seed` |
| `0x122CA0` | `0x050290` | `0x555758` | `gfxModelBase__LoadMod_datBaseTokenizer__ref__int_unsigned_int_bool_int_gfxShaderFactory__ptr` | 976 | 432 | -544 | `seed` |
| `0x123240` | `0x3342D0` | `0x564790` | `mcPlaneSplash__FileIO_datParser__ref` | 288 | 283 | -5 | `seed` |
| `0x123DB0` | `0x334EB0` | `0x566700` | `mcRain__FileIO_datParser__ref` | 576 | 563 | -13 | `seed` |
| `0x12C4E0` | `0x3656E0` | `0x5A4E28` | `mcTriggerArrayFactory__LoadTriggerEvents_datAsciiTokenizer__ref__atArray_mcTriggerEvent__ptr__8_unsigned_short_65535__ref` | 208 | 196 | -12 | `seed` |
| `0x12C5B0` | `0x3657B0` | `0x5A48B8` | `mcTriggerArrayFactory__LoadLineTrigger_datAsciiTokenizer__ref` | 64 | 96 | +32 | `seed` |
| `0x12C5F0` | `0x365810` | `0x5A4928` | `mcTriggerArrayFactory__LoadCircleTrigger_datAsciiTokenizer__ref` | 64 | 124 | +60 | `seed` |
| `0x12C630` | `0x365890` | `0x5A49B0` | `mcTriggerArrayFactory__LoadTimerTrigger_datAsciiTokenizer__ref` | 64 | 96 | +32 | `seed` |
| `0x12C670` | `0x3658F0` | `0x5A4790` | `mcTriggerArrayFactory__LoadTrigger_datAsciiTokenizer__ref__int_atArray_mcTrigger__ptr__8_unsigned_short_65535__ref` | 160 | 189 | +29 | `seed` |
| `0x12C740` | `0x364300` | `0x5A37E0` | `mcTrigger__LoadTriggeredByData_datAsciiTokenizer__ref` | 176 | 210 | +34 | `seed` |
| `0x12C870` | `0x3644F0` | `-` | `mcTrigger__LoadTriggerLapData_datAsciiTokenizer__ref` | 96 | 93 | -3 | `prop_round_2` |
| `0x130630` | `0x09D710` | `0x25CC60` | `mcConditionVariables__FileIO_datParser__ref` | 688 | 1050 | +362 | `seed` |
| `0x130AD0` | `0x093440` | `0x24CCE8` | `lightGlowCondition__FileIO_datParser__ref` | 208 | 195 | -13 | `seed` |
| `0x130EE0` | `0x093810` | `-` | `mcGlow__FileIO_datParser__ref` | 48 | 42 | -6 | `insn_signature` |
| `0x130F10` | `0x093840` | `0x24D8F8` | `mcGlow__FileIO_datParser__ref` | 576 | 1076 | +500 | `seed` |
| `0x136BB0` | `0x1A46C0` | `0x39F6F8` | `mcOccluderSystem__LoadHeader_datAsciiTokenizer__ref__int__ptr__mcOccluderPolyhedron__ptr__ptr__int__ptr__mcOccluderPoly__ptr__ptr` | 80 | 155 | +75 | `seed` |
| `0x136C20` | `-` | `0x39EF20` | `mcOccluderSystem__Load_datAsciiTokenizer__ref__int__ptr__mcOccluderPolyhedron__ptr__ptr__int__ptr__mcOccluderPoly__ptr__ptr` | 48 | 0 | +0 | `ps2_callgraph` |
| `0x1376A0` | `0x09E3C0` | `0x25C7C8` | `mcSkyHatClass__FileIO_datParser__ref` | 400 | 347 | -53 | `seed` |
| `0x13B5B0` | `0x0A1D00` | `-` | `mcStarField__FileIO_datParser__ref` | 32 | 32 | +0 | `prop_round_2` |
| `0x13B5D0` | `0x0A1D20` | `0x25CAF0` | `mcStarField__FileIO_datParser__ref` | 64 | 63 | -1 | `seed` |
| `0x13D7E0` | `0x358340` | `0x595B18` | `mcLightData__FileIO_datParser__ref` | 480 | 467 | -13 | `seed` |
| `0x13E510` | `0x327670` | `0x553388` | `mcPowerupTuneData__FileIO_datParser__ref` | 400 | 440 | +40 | `seed` |
| `0x13FD80` | `0x329380` | `0x552EA0` | `mcPowerUpSourceFactory__LoadAttributes_mcPowerUpSource__ref__datAsciiTokenizer__ref` | 304 | 318 | +14 | `seed` |
| `0x13FEB0` | `0x3294C0` | `0x5530A8` | `mcPowerUpSourceFactory__LoadPowerUpTypes_mcPowerUpSource__ref__datAsciiTokenizer__ref` | 176 | 176 | +0 | `seed` |
| `0x140010` | `0x329760` | `0x552DF0` | `mcPowerUpSourceFactory__LoadPowerUp_mcPowerUpSource__ref__datAsciiTokenizer__ref__bool` | 96 | 227 | +131 | `seed` |
| `0x1419A0` | `0x21BDC0` | `0x450240` | `sndSurfaceSoundListEntry__FileIO_datParser__ref` | 128 | 149 | +21 | `seed` |
| `0x141D70` | `0x21CA50` | `0x44ECD0` | `sndImpactSoundData__FileIO_datParser__ref` | 224 | 280 | +56 | `seed` |
| `0x142950` | `0x21CEC0` | `0x44F6D0` | `sndSoundFxList__LoadData_datTokenizer__ref` | 336 | 328 | -8 | `seed` |
| `0x142BB0` | `0x21D120` | `0x44FB30` | `sndSoundFxSetup__LoadData_datTokenizer__ref` | 64 | 59 | -5 | `prop_round_1` |
| `0x1455A0` | `0x352070` | `0x58BEA0` | `mcSndControl3dMultiple__LoadDataNoPosition_datTokenizer__ref` | 352 | 402 | +50 | `seed` |
| `0x145880` | `0x3523D0` | `0x58C618` | `mcSoundFxArea__LoadData_datTokenizer__ref` | 144 | 132 | -12 | `seed` |
| `0x14BB00` | `0x1AFBB0` | `0x3AF620` | `mcNetProtocol__CommandToString_int` | 544 | 516 | -28 | `seed` |
| `0x14EB40` | `0x26B770` | `0x4BE1C8` | `mcRaceConfig__LoadInfo_datAsciiTokenizer__ref` | 320 | 358 | +38 | `seed` |
| `0x1500D0` | `0x26F620` | `0x4B8DB0` | `mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref` | 656 | 219 | -437 | `seed` |
| `0x150AA0` | `0x26F010` | `0x4B7C38` | `mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref` | 1280 | 736 | -544 | `career_semantic_seed` |
| `0x151000` | `-` | `0x4B7900` | `mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x1532C0` | `0x289D80` | `0x4D4750` | `mcUnlocking__IsSlipstreamTurboUnlocked_bool_const` | 80 | 80 | +0 | `career_callgraph` |
| `0x15B1B0` | `0x052540` | `0x1EFD90` | `swPtxBirth__FileIO_datParser__ref` | 703 | 798 | +95 | `seed` |
| `0x15E660` | `0x203BF0` | `0x5CA3A0` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___find_uiStaticString_const__ref` | 128 | 126 | -2 | `prop_round_2` |
| `0x15FA30` | `0x205350` | `0x5C8B40` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_atPtr_uiWidget__Select1st_pair_uiStaticString_const_atPtr_uiWidget_less_uiStaticString_allocator_atPtr_uiWidget___insert_unique_pair_uiStaticString_const_atPtr_uiWidget_const__ref` | 272 | 285 | +13 | `prop_round_4` |
| `0x15FC00` | `0x205590` | `0x5CA818` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___insert_unique_pair_uiStaticString_const_unsigned_int_const__ref` | 272 | 285 | +13 | `prop_round_2` |
| `0x1650B0` | `0x200C20` | `0x41FBA8` | `uiGroupBase__FileIO_datParser__ref` | 16 | 11 | -5 | `seed` |
| `0x165310` | `0x207910` | `0x4257B8` | `uiVisual__FileIO_datParser__ref` | 144 | 132 | -12 | `seed` |
| `0x1654A0` | `0x207A90` | `0x425D48` | `uiVisualWithBlendColor__FileIO_datParser__ref` | 96 | 86 | -10 | `seed` |
| `0x165C10` | `0x2082E0` | `0x424A68` | `uiText__FileIO_datParser__ref` | 112 | 107 | -5 | `prop_round_1` |
| `0x165C80` | `0x208350` | `0x424B20` | `uiText__FileIO_datParser__ref` | 544 | 529 | -15 | `seed` |
| `0x167610` | `0x2091B0` | `0x424260` | `uiTable__FileIO_datParser__ref` | 608 | 607 | -1 | `seed` |
| `0x168C30` | `-` | `0x422F70` | `uiCopyingString__Set_char_const__ptr__int` | 224 | 0 | +0 | `ps2_callgraph` |
| `0x168D10` | `-` | `0x423090` | `uiCopyingString__SetAlreadyAllocated_char_const__ptr` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x169590` | `0x0AD3B0` | `0x267788` | `vehTransTune__FileIO_datParser__ref` | 288 | 230 | -58 | `seed` |
| `0x1703D0` | `0x0A6DA0` | `0x26B0C8` | `vehWheelTune__FileIO_datParser__ref` | 496 | 563 | +67 | `seed` |
| `0x171610` | `0x0ACA70` | `0x263258` | `vehEngineTune__FileIO_datParser__ref` | 224 | 230 | +6 | `seed` |
| `0x1721D0` | `0x35EC80` | `0x59F848` | `vehStuckTune__FileIO_datParser__ref` | 160 | 145 | -15 | `seed` |
| `0x1728E0` | `0x3606F0` | `0x59D7C0` | `vehGyroTune__FileIO_datParser__ref` | 224 | 211 | -13 | `seed` |
| `0x172F80` | `0x0AC0A0` | `0x26BCB0` | `vehAeroTune__FileIO_datParser__ref` | 128 | 123 | -5 | `seed` |
| `0x175F80` | `0x0ADEE0` | `0x262510` | `vehDrivetrainTune__FileIO_datParser__ref` | 80 | 76 | -4 | `seed` |
| `0x1763D0` | `0x0AE920` | `0x26C530` | `vehAxleTune__FileIO_datParser__ref` | 64 | 54 | -10 | `seed` |
| `0x17C070` | `0x357410` | `0x594B40` | `vehTrackCS__FileIO_datParser__ref` | 752 | 790 | +38 | `seed` |
| `0x17CFD0` | `0x357FF0` | `0x5916D0` | `vehPovCS__FileIO_datParser__ref` | 208 | 194 | -14 | `seed` |
| `0x17D990` | `0x138800` | `-` | `camViewCS__FileIO_datParser__ref` | 64 | 57 | -7 | `insn_signature` |
| `0x17D9D0` | `0x138840` | `0x31F3A0` | `camViewCS__FileIO_datParser__ref` | 80 | 79 | -1 | `seed` |
| `0x17DB90` | `0x138470` | `0x31EEC0` | `camBaseCS__FileIO_datParser__ref` | 144 | 160 | +16 | `seed` |
| `0x17E9D0` | `0x362790` | `0x5A24A0` | `camAppCS__FileIO_datParser__ref` | 384 | 369 | -15 | `seed` |
| `0x18FF60` | `0x2A4E00` | `0x4D8B28` | `phArchetype__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 184 | 343 | +159 | `seed` |
| `0x190150` | `0x2A5060` | `0x4D9028` | `phArchetypePhys__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 400 | 441 | +41 | `seed` |
| `0x190350` | `0x2A5340` | `0x4D95C0` | `phArchetypeDamp__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 432 | 496 | +64 | `seed` |
| `0x190810` | `0x2A5990` | `-` | `phArchetype__Load_datAsciiTokenizer__ref__phBound__ptr` | 119 | 177 | +58 | `insn_signature` |
| `0x19B730` | `0x2CB0C0` | `-` | `mcTimeWarperTune__FileIO_datParser__ref` | 32 | 24 | -8 | `insn_signature` |
| `0x19E590` | `-` | `0x4A5CB8` | `phQuadtreeCell__ReadCells_datAsciiTokenizer__ref__int` | 240 | 0 | +0 | `ps2_callgraph` |
| `0x19EAD0` | `0x234DF0` | `0x47E630` | `phBound__Load_datAsciiTokenizer__ref` | 544 | 599 | +55 | `seed` |
| `0x19ECF0` | `-` | `0x47E8A8` | `WriteHeader_110_datAsciiTokenizer__ref__phBound__ptr` | 157 | 0 | +0 | `ps2_callgraph` |
| `0x1A4150` | `0x2367C0` | `0x4A1380` | `phForceSphere__Load_v110_datAsciiTokenizer__ref` | 320 | 465 | +145 | `seed` |
| `0x1A4290` | `0x2369A0` | `0x4A15E0` | `phForceSphere__Load_v110_datBinTokenizer__ref` | 288 | 310 | +22 | `seed` |
| `0x1A53F0` | `0x231B30` | `0x482110` | `phBoundOTGrid__LoadDef_v110_datAsciiTokenizer__ref` | 160 | 151 | -9 | `seed` |
| `0x1A8480` | `0x2303F0` | `0x475888` | `phBoundComposite__Load_v110_datAsciiTokenizer__ref` | 720 | 897 | +177 | `seed` |
| `0x1AE860` | `0x2508F0` | `0x46D8F0` | `phBoundBox__Load_v110_datAsciiTokenizer__ref` | 233 | 298 | +65 | `seed` |
| `0x1B2078` | `0x2398C0` | `0x478CB0` | `phBoundGeometry__Load_v110_datAsciiTokenizer__ref` | 2333 | 1855 | -478 | `seed` |
| `0x1B29A0` | `0x23A4F0` | `-` | `phBoundGeometry__Load_datAsciiTokenizer__ref__int` | 3454 | 2746 | -708 | `seed` |
| `0x1BFDC0` | `-` | `0x5CF2A8` | `phPolytree_phQuadtreeCell___ReadCells_datAsciiTokenizer__ref__phBoundGeometry_const__ptr__int_Vector3_const__ref__Vector3_const__ref` | 144 | 0 | +0 | `ps2_callgraph` |
| `0x1C00F0` | `-` | `0x493EA8` | `phBoundQuadtree__LoadCells_datAsciiTokenizer__ref__int_int_int_int_float_Vector3_const__ref__Vector3_const__ref` | 112 | 0 | +0 | `ps2_callgraph` |
| `0x1C0160` | `0x248020` | `0x493F70` | `phBoundQuadtree__Load_v110_datAsciiTokenizer__ref` | 368 | 394 | +26 | `seed` |
| `0x1C2C30` | `0x23F080` | `0x47EC70` | `phBoundOctree__LoadCells_datAsciiTokenizer__ref__int_int_int_int_float_Vector3_const__ref__Vector3_const__ref` | 240 | 312 | +72 | `seed` |
| `0x1CCC90` | `0x2529A0` | `0x47DCD8` | `phBoundHotdog__Load_v110_datAsciiTokenizer__ref` | 256 | 190 | -66 | `seed` |
| `0x1CE3B0` | `0x1A7260` | `-` | `phSurface__SaveData_datAsciiTokenizer__ref` | 16 | 11 | -5 | `prop_round_2` |
| `0x1CE4C0` | `0x1A7360` | `0x3A9280` | `phSurface__SaveData_datAsciiTokenizer__ref` | 400 | 392 | -8 | `seed` |
| `0x1D1AC0` | `0x1A6BF0` | `-` | `phMaterial__Save_datAsciiTokenizer__ref` | 272 | 255 | -17 | `prop_round_1` |
| `0x1D1BD0` | `-` | `0x3A3410` | `phMaterial__LoadData_datAsciiTokenizer__ref` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x1D1C10` | `0x1A6D30` | `0x3A3488` | `phMaterial__Save_datAsciiTokenizer__ref` | 128 | 113 | -15 | `seed` |
| `0x1D1CB0` | `0x1A6DD0` | `0x3A35A0` | `phMaterial__SaveData_datAsciiTokenizer__ref` | 112 | 101 | -11 | `seed` |
| `0x1D1E10` | `0x1A6F10` | `0x3A3860` | `phMaterialSnd__LoadData_datAsciiTokenizer__ref` | 128 | 151 | +23 | `seed` |
| `0x1D1EC0` | `0x1A6FF0` | `0x3A3970` | `phMaterialSnd__SaveData_datAsciiTokenizer__ref` | 112 | 109 | -3 | `seed` |
| `0x1D4BF0` | `0x218220` | `0x4489F0` | `sndBank__AddStream_char_const__ptr__bool_bool` | 336 | 425 | +89 | `seed` |
| `0x1D6AF0` | `0x21B0C0` | `0x44E098` | `sndControlVolumeGroup__FileIOInternal_datParser__ref` | 80 | 79 | -1 | `seed` |
| `0x1DEA50` | `0x3530B0` | `0x58DC18` | `crSkeletonData__Load_Stream__ptr__char_const__ptr` | 352 | 503 | +151 | `seed` |
| `0x1DEDE0` | `0x353480` | `0x58CAA8` | `crBoneData__Load_v100_datTokenizer__ref__crBoneData__ptr__ptr__int__ref` | 352 | 465 | +113 | `seed` |
| `0x1DEF40` | `0x353660` | `0x58CDD0` | `ReadDOF_datTokenizer__ref__unsigned_short__ref__unsigned_short_unsigned_short_float__ref__float__ref__float__ref` | 128 | 118 | -10 | `seed` |
| `0x1DEFE0` | `0x353700` | `0x58CF68` | `crBoneData__Load_v101_datTokenizer__ref__crBoneData__ptr__ptr__int__ref` | 800 | 961 | +161 | `seed` |
| `0x1DF360` | `0x0EAAE0` | `0x2BBAB8` | `txtFontTexGlyph__Load_Stream__ptr` | 112 | 101 | -11 | `seed` |
| `0x1DF400` | `0x0EAE40` | `-` | `txtFontTex__Draw_float_float_unsigned_wchar_t_const__ptr__float_float_txtCursor__ptr__bool_txtDrawBuffer__ptr` | 381 | 2878 | +2497 | `prop_round_1` |
| `0x1E0340` | `0x0EAB70` | `0x2BBE00` | `txtFontTex__Init_int_char_const__ptr` | 352 | 405 | +53 | `seed` |
| `0x1E04A0` | `0x0EBDA0` | `0x2BC098` | `txtFontTex__Load_char_const__ptr__bool` | 992 | 837 | -155 | `seed` |
| `0x1E0A90` | `0x0EC0F0` | `-` | `txtFontTex__ComputeExtents_int__ptr__int__ptr__unsigned_wchar_t_const__ptr__float_float_txtCursor__ptr` | 112 | 100 | -12 | `insn_signature` |
| `0x1E0E70` | `0x0EC2F0` | `0x2BB880` | `txtGetFontTex_char_const__ptr__bool` | 320 | 275 | -45 | `seed` |
| `0x1E0FB0` | `-` | `0x2BDE60` | `txtStringData__txtStringData_void` | 48 | 0 | +0 | `ps2_callgraph` |
| `0x1E0FE0` | `-` | `0x2BDE98` | `txtStringData__dtor_txtStringData_void` | 19 | 0 | +0 | `ps2_callgraph` |
| `0x1E1020` | `-` | `0x2BDF20` | `txtStringData__Load_Stream__ptr__unsigned_int` | 256 | 0 | +0 | `ps2_callgraph` |
| `0x1E1170` | `0x0EA480` | `0x2BE210` | `txtStringTable__Load_char_const__ptr__txtLanguage__eLanguage_unsigned_int_bool_bool` | 608 | 655 | +47 | `seed` |
| `0x1E1410` | `0x0EA750` | `-` | `txtStringTable__Get_char_const__ptr` | 432 | 461 | +29 | `seed` |
| `0x1E1E60` | `0x361370` | `0x5A0678` | `txtMovieSubtitles__FileIO_datParser__ref` | 96 | 88 | -8 | `seed` |
| `0x1E2260` | `-` | `0x2BECA0` | `txtHashEntry__txtHashEntry_unsigned_int_txtStringData__ptr__txtHashEntry__ptr` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x1E2450` | `0x32F7D0` | `0x55F540` | `datParser__datParser_char_const__ptr` | 64 | 105 | +41 | `seed` |
| `0x1E2490` | `0x32F840` | `-` | `datParser__dtor_datParser_void` | 48 | 109 | +61 | `prop_round_2` |
| `0x1E24E0` | `0x32F3D0` | `0x55F7C0` | `datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr` | 160 | 184 | +24 | `seed` |
| `0x1E28B0` | `0x32F8B0` | `0x55F738` | `datParser__AddParser_char_const__ptr__datCallback__ptr` | 80 | 81 | +1 | `seed` |
| `0x1E2EB0` | `0x0DCB40` | `0x55F498` | `parFileIO__SetName_char_const__ptr` | 48 | 22 | -26 | `seed` |
| `0x1E2EE0` | `0x32FF00` | `0x55F4F0` | `parFileIO__GetTypeName_void` | 16 | 39 | +23 | `seed` |
| `0x1E2EF0` | `0x32FF50` | `0x55F268` | `parFileIO__parFileIO_void` | 32 | 17 | -15 | `seed` |
| `0x1E3A30` | `0x05DF69` | `0x2003A8` | `netProtocol__CommandToString_int` | 320 | 210 | -110 | `seed` |
| `0x1E7D70` | `0x136820` | `0x31B518` | `gfxEdgeModel__Load_datBaseTokenizer__ref` | 4816 | 4936 | +120 | `seed` |
| `0x1EE370` | `0x0E1750` | `0x2B06B8` | `rmcShaderTemplate__Load_datTokenizer__ref` | 416 | 200 | -216 | `seed` |
| `0x1EEC00` | `0x32C0B0` | `0x1EBFC0` | `mshMesh__LoadMod_datBaseTokenizer__ref__bool_int` | 3488 | 5813 | +2325 | `seed` |
| `0x1F17A0` | `0x0EBC90` | `0x2BDB70` | `txtFontTex__SetBilinear_bool` | 16 | 74 | +58 | `seed` |
| `0x1F8600` | `0x2B42C0` | `0x4FBDD8` | `inflate_blocks_new_z_stream_s__ptr__unsigned_long__ptr__unsigned_long_unsigned_char_const__ptr__unsigned_int_unsigned_int` | 80 | 72 | -8 | `seed` |
| `0x1F8B50` | `0x2B4810` | `0x4FBD28` | `inflate_blocks_reset_inflate_blocks_state__ptr__z_stream_s__ptr__unsigned_long__ptr` | 128 | 123 | -5 | `seed` |
| `0x1F8C70` | `0x2B4930` | `0x4FBEC0` | `inflate_blocks_inflate_blocks_state__ptr__z_stream_s__ptr__int` | 2930 | 2929 | -1 | `seed` |
| `0x1F9990` | `0x2B56A0` | `0x4FE068` | `inflate_flush_inflate_blocks_state__ptr__z_stream_s__ptr__int` | 64 | 57 | -7 | `seed` |
| `0x1F99D0` | `0x2B56E0` | `0x4FCB38` | `inflate_codes_inflate_blocks_state__ptr__z_stream_s__ptr__int` | 1808 | 1804 | -4 | `seed` |
| `0x1FA0E0` | `0x2B5DF0` | `0x4FD340` | `inflate_codes_free_inflate_codes_state__ptr__z_stream_s__ptr` | 32 | 20 | -12 | `seed` |
| `0x1FA5F0` | `0x2B6300` | `0x4FDD40` | `inflate_trees_bits_unsigned_int__ptr__unsigned_int__ptr__inflate_huft_s__ptr__ptr__inflate_huft_s__ptr__z_stream_s__ptr` | 176 | 163 | -13 | `seed` |
| `0x1FA6A0` | `0x2B63B0` | `0x4FDE40` | `inflate_trees_dynamic_unsigned_int_unsigned_int_unsigned_int__ptr__unsigned_int__ptr__unsigned_int__ptr__inflate_huft_s__ptr__ptr__inflate_huft_s__ptr__ptr__inflate_huft_s__ptr__z_stream_s__ptr` | 400 | 387 | -13 | `seed` |
| `0x1FA830` | `0x2B6540` | `0x4FCAC0` | `inflate_codes_new_unsigned_int_unsigned_int_inflate_huft_s__ptr__inflate_huft_s__ptr__z_stream_s__ptr` | 48 | 46 | -2 | `seed` |
| `0x1FA860` | `0x2B6570` | `0x4FE030` | `inflate_trees_fixed_unsigned_int__ptr__unsigned_int__ptr__inflate_huft_s__ptr__ptr__inflate_huft_s__ptr__ptr__z_stream_s__ptr` | 304 | 298 | -6 | `seed` |
| `0x208D30` | `0x20CE80` | `-` | `StringNormalize_char__ptr__char_const__ptr` | 48 | 45 | -3 | `insn_signature` |
| `0x208DB0` | `0x20CF80` | `0x433228` | `StringDuplicate_char_const__ptr` | 64 | 63 | -1 | `seed` |
| `0x208E10` | `0x20CFD0` | `-` | `ConstString__vCopy_char_const__ptr` | 32 | 86 | +54 | `prop_round_1` |
| `0x209490` | `0x20EE80` | `0x433B48` | `datBaseTokenizer__Init_char_const__ptr__Stream__ptr` | 48 | 45 | -3 | `seed` |
| `0x2094C0` | `0x20EEB0` | `0x433B78` | `datBaseTokenizer__PushBack_char_const__ptr__int` | 80 | 117 | +37 | `seed` |
| `0x209580` | `0x20EFE0` | `0x433DD0` | `datBaseTokenizer__GetToken_char__ptr__int` | 448 | 723 | +275 | `seed` |
| `0x209740` | `0x20F2C0` | `0x434060` | `datBaseTokenizer__MatchToken_char_const__ptr` | 32 | 26 | -6 | `seed` |
| `0x209760` | `0x20F2E0` | `0x4340A8` | `datBaseTokenizer__MatchIToken_char_const__ptr` | 48 | 47 | -1 | `seed` |
| `0x209790` | `0x20F310` | `0x4340F0` | `datBaseTokenizer__CheckToken_char_const__ptr__bool` | 176 | 171 | -5 | `seed` |
| `0x209840` | `0x20F3C0` | `0x4341B0` | `datBaseTokenizer__CheckIToken_char_const__ptr__bool` | 144 | 138 | -6 | `seed` |
| `0x209A10` | `0x20F6A0` | `0x434630` | `datAsciiTokenizer__GetInt_void` | 64 | 56 | -8 | `seed` |
| `0x209A50` | `0x20F6E0` | `0x434690` | `datAsciiTokenizer__GetFloat_void` | 80 | 64 | -16 | `seed` |
| `0x209AA0` | `0x20F720` | `-` | `datAsciiTokenizer__GetVector_Vector2__ref` | 32 | 30 | -2 | `prop_round_1` |
| `0x209AC0` | `0x20F740` | `0x434758` | `datAsciiTokenizer__GetVector_Vector3__ref` | 48 | 22 | -26 | `seed` |
| `0x209B20` | `0x20F7B0` | `-` | `datAsciiTokenizer__GetVector_Vector4__ref` | 64 | 50 | -14 | `prop_round_1` |
| `0x209B70` | `0x20F7F0` | `-` | `datAsciiTokenizer__MatchInt_char_const__ptr` | 32 | 39 | +7 | `prop_round_1` |
| `0x209ED0` | `0x20FBA0` | `0x4352D8` | `datAsciiTokenizer__Put_Vector4_const__ref` | 96 | 61 | -35 | `seed` |
| `0x209F30` | `0x20FD50` | `0x435360` | `datAsciiTokenizer__Put_Vector3_const__ref` | 96 | 88 | -8 | `seed` |
| `0x209F90` | `0x20FDB0` | `0x435400` | `datAsciiTokenizer__Put_Vector4_const__ref` | 96 | 95 | -1 | `seed` |
| `0x20A060` | `0x20FE80` | `0x435540` | `datBinTokenizer__GetInt_void` | 48 | 37 | -11 | `seed` |
| `0x20A510` | `0x2103E0` | `-` | `datMultiTokenizer__datMultiTokenizer_void` | 32 | 29 | -3 | `insn_signature` |
| `0x20A530` | `0x210400` | `-` | `datTokenizer__datTokenizer_void` | 32 | 19 | -13 | `insn_signature` |
| `0x20A550` | `0x210420` | `0x435BD8` | `datTokenizer__datTokenizer_char_const__ptr__Stream__ptr` | 48 | 59 | +11 | `seed` |
| `0x20A720` | `0x20D190` | `-` | `datAssetManager__SetPath_char_const__ptr` | 32 | 22 | -10 | `insn_signature` |
| `0x20AA20` | `-` | `0x46CB40` | `phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x20AA60` | `0x20D6F0` | `-` | `datAssetManager__Open_char_const__ptr__char_const__ptr__bool_bool` | 64 | 266 | +202 | `prop_round_3` |
| `0x20AB10` | `-` | `0x435C10` | `_TStringDuplicate_unsigned_wchar_t_const__ptr` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x20BC20` | `0x1A20B0` | `0x399860` | `Stream__Flush_void` | 128 | 115 | -13 | `seed` |
| `0x20BCE0` | `0x1A2180` | `0x399098` | `Stream__AllocStream_char_const__ptr__int_coreFileMethods_const__ptr` | 128 | 243 | +115 | `seed` |
| `0x20BF10` | `0x1A23A0` | `0x3993A8` | `Stream__Read_void__ptr__int` | 288 | 288 | +0 | `seed` |
| `0x20C030` | `0x1A24C0` | `0x399538` | `Stream__Write_void_const__ptr__int` | 224 | 216 | -8 | `prop_round_1` |
| `0x20C110` | `0x1A25A0` | `-` | `datBaseTokenizer__GetTokenCh_void` | 32 | 30 | -2 | `prop_round_2` |
| `0x20C150` | `0x1A25E0` | `0x3996C0` | `Stream__Seek_int` | 80 | 67 | -13 | `seed` |
| `0x20C1A0` | `0x1A2630` | `0x399748` | `Stream__Close_void` | 64 | 51 | -13 | `seed` |
| `0x20C1E0` | `0x1A2670` | `-` | `Stream__Size_void` | 96 | 92 | -4 | `insn_signature` |
| `0x20C290` | `-` | `0x399B40` | `Stream__CreateMemoryStream_char_const__ptr__void__ptr__int_bool_bool` | 48 | 0 | +0 | `ps2_callgraph` |
| `0x20C320` | `0x1A2780` | `0x399A70` | `Stream__PreLoad_Stream__ptr` | 192 | 239 | +47 | `seed` |
| `0x20C530` | `0x1A1C00` | `-` | `ipcTime_void` | 32 | 20 | -12 | `insn_signature` |
| `0x2A0790` | `0x1A1D40` | `-` | `ipcCriticalSection__ipcCriticalSection_ipcCriticalSectionToken__ref` | 11 | 27 | +16 | `prop_round_1` |
| `0x2CE24C` | `0x3C1310` | `-` | `XDK::CDirectSoundStream_AddRef` | 71 | 71 | +0 | `insn_signature` |
| `0x2CE293` | `0x3C1357` | `-` | `XDK::CDirectSoundStream_Release` | 78 | 78 | +0 | `insn_signature` |
| `0x2CE2E1` | `0x3C13A5` | `-` | `XDK::CDirectSoundStream_GetInfo` | 103 | 103 | +0 | `insn_signature` |
| `0x2CE348` | `0x3C140C` | `-` | `XDK::CDirectSoundStream_Discontinuity` | 77 | 77 | +0 | `insn_signature` |
| `0x2CE395` | `0x3C1459` | `-` | `XDK::CDirectSoundStream_Flush` | 75 | 75 | +0 | `insn_signature` |
| `0x2CE3E0` | `0x3C14A4` | `-` | `XDK::CDirectSoundStream_GetStatus` | 81 | 81 | +0 | `insn_signature` |
| `0x2CE431` | `0x3C14F5` | `-` | `XDK::CDirectSoundStream_Process` | 200 | 200 | +0 | `insn_signature` |
| `0x2D1491` | `0x3C391A` | `-` | `XDK::DirectSoundCreateStream` | 87 | 87 | +0 | `insn_signature` |
| `0x305B80` | `0x415130` | `-` | `XDK::D3DDevice_SetStreamSource` | 144 | 140 | -4 | `insn_signature` |
