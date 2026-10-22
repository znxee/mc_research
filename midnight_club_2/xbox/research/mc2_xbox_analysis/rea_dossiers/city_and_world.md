# REA Dossier: City Registration, Lighting, ModelInfo & Environment (`city_and_world`)

- **REA Evidence ID:** `ev_6ed4ef121c1de9e59f59833739f0b079d99cee70e89f477e1a1877a2dd342145`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 34
- **Hex-Rays Decompiled Functions:** 17

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

### `mc__mcCityData__mcCityData_void`
- **MC2 Xbox VA:** `0x083650..0x83717` (208 B) | **MC3 Xbox VA:** `0x26ED10` (754 B, delta: `+546 B`) | **MC3 PS2 VA:** `0x4B7600`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_6b73a142c1ff4b4b996473303ee8084a9736914a71fd990611789088a6d64fcb`

```cpp
int mc__mcCityData__mcCityData_void()
{
  int v0; // ebp
  int v1; // eax
  int v2; // ebx
  int result; // eax
  const char *v4; // [esp-4h] [ebp-54h]
  _BYTE v5[64]; // [esp+10h] [ebp-40h] BYREF

  v0 = sub_82EA0();
  v1 = _builtin_new(132);
  if ( v1 )
    v2 = sub_169360(v1);
  else
    v2 = 0;
  if ( !strcmp("losangeles", off_34F2E4[dword_3ACD38]) )
  {
    strlen(v5, 64, "l_props_particle");
  }
  else if ( !strcmp("paris", off_34F2E4[dword_3ACD38]) )
  {
    strlen(v5, 64, "p_props_particle");
  }
  else
  {
    if ( !strcmp("tokyo", off_34F2E4[dword_3ACD38]) )
      v4 = "t_shared_particle";
    else
      v4 = "l_props_particle";
    strlen(v5, 64, v4);
  }
  result = (*(int (__thiscall **)(int, _DWORD, _BYTE *))(*(_DWORD *)v2 + 4))(v2, *(_DWORD *)(v0 + 72), v5);
  *(_DWORD *)(v0 + 112) = v2;
  return result;
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

### `mcLightning__initStaticData_void`
- **MC2 Xbox VA:** `0x120E00..0x120e17` (32 B) | **MC3 Xbox VA:** `0x03B0E0` (23 B, delta: `-9 B`) | **MC3 PS2 VA:** `0x1D2588`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_2a7be2c00619d1509d103d1f5470f46590b66161fbde232e6cf26fadf2e167ff`

```cpp
int mcLightning__initStaticData_void()
{
  int result; // eax

  result = swPtxBirth__Load_char_const__ptr__unsigned_char("fx_lightning", 1, 0);
  dword_39A26C = result;
  return result;
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

### `mcCity__InitGlobalLighting_char_const__ptr`
- **MC2 Xbox VA:** `0x12EB30..0x12eddf` (426 B) | **MC3 Xbox VA:** `0x09BE10` (914 B, delta: `+488 B`) | **MC3 PS2 VA:** `0x258E18`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_a5d1393baec634856c25814928a9b084b6cc2f8d8a92b0120b07a41daad8f0c8`

```cpp
int __thiscall mcCity__InitGlobalLighting_char_const__ptr(float *this, int a2)
{
  float *v2; // esi
  int Data_datBinTokenizer__ref__phBound__FileVersion; // edi
  unsigned __int8 v5; // c0
  unsigned __int8 v6; // c2
  float v7; // eax
  float v8; // edx
  unsigned __int8 v10; // c0
  unsigned __int8 v11; // c2
  float v12; // ecx
  float v13; // eax
  _DWORD *v14; // ecx
  float v16; // [esp+Ch] [ebp-1B4h] BYREF
  float v17; // [esp+10h] [ebp-1B0h]
  float v18; // [esp+14h] [ebp-1ACh]
  float *v19; // [esp+18h] [ebp-1A8h]
  int v20; // [esp+1Ch] [ebp-1A4h]
  char v21[256]; // [esp+C0h] [ebp-100h] BYREF

  v2 = this;
  v19 = this;
  Data_datBinTokenizer__ref__phBound__FileVersion = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
                                                      a2,
                                                      "global_lighting",
                                                      "gt",
                                                      0,
                                                      1);
  v20 = Data_datBinTokenizer__ref__phBound__FileVersion;
  if ( Data_datBinTokenizer__ref__phBound__FileVersion )
  {
    v2[250] = 0.0;
    v2[249] = 0.0;
    v2[248] = 0.0;
    v2[253] = 0.0;
    v2[252] = 0.0;
    v2[251] = 0.0;
    datTokenizer__datTokenizer_char_const__ptr__Stream__ptr(
      "global_lighting",
      Data_datBinTokenizer__ref__phBound__FileVersion);
    if ( datBaseTokenizer__GetToken_char__ptr__int(v21, 256) )
    {
      do
      {
        if ( !strcmp(v21, "ambient") )
        {
          datBaseTokenizer__MatchToken_char_const__ptr("{");
          datBaseTokenizer__MatchToken_char_const__ptr("color:");
          datAsciiTokenizer__GetVector_Vector3__ref(&v16);
          datBaseTokenizer__MatchToken_char_const__ptr("}");
          if ( v5 | v6 )
          {
            v7 = v17;
            v2[248] = v16;
            v8 = v18;
            v2[249] = v7;
            v2[250] = v8;
          }
        }
        else
        {
          if ( strcmp(v21, "directional") )
            strcmp("bad global lighting file");
          datBaseTokenizer__MatchToken_char_const__ptr("{");
          datBaseTokenizer__MatchToken_char_const__ptr("color:");
          datAsciiTokenizer__GetVector_Vector3__ref(&v16);
          datBaseTokenizer__MatchToken_char_const__ptr("direction:");
          if ( v10 | v11 )
          {
            v12 = v17;
            v2[251] = v16;
            v13 = v18;
            v2[252] = v12;
            v14 = v19 + 254;
            v2[253] = v13;
            datAsciiTokenizer__GetVector_Vector3__ref(v14);
          }
          else
          {
            datAsciiTokenizer__GetVector_Vector3__ref(&v16);
          }
          datBaseTokenizer__MatchToken_char_const__ptr("}");
        }
      }
      while ( datBaseTokenizer__GetToken_char__ptr__int(v21, 256) );
      v2 = v19;
      Data_datBinTokenizer__ref__phBound__FileVersion = v20;
    }
    Stream__Close_void(Data_datBinTokenizer__ref__phBound__FileVersion);
  }
  else
  {
    v2[248] = 0.1;
    v2[249] = 0.1;
    v2[250] = 0.1;
    v2[251] = 0.1;
    v2[252] = 0.1;
    v2[253] = 0.1;
    v2[254] = 0.1;
    v2[255] = 0.1;
    v2[256] = 0.1;
  }
  return sub_6F900(v2 + 254);
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

### `mcCityEnvMap__LoadCondition_void`
- **MC2 Xbox VA:** `0x138860..0x1388ab` (80 B) | **MC3 Xbox VA:** `0x3319B0` (77 B, delta: `-3 B`) | **MC3 PS2 VA:** `0x562450`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_6ff03981ec883665f1157ceac09396d60589836fa31fc6b9bfeea6af0d3caee8`

```cpp
int __thiscall mcCityEnvMap__LoadCondition_void(_DWORD *this)
{
  int result; // eax
  _BYTE v3[64]; // [esp+4h] [ebp-40h] BYREF

  strlen(v3, 64, "fx_envmapbk_%s_%s", off_34F3B8[dword_3ACD3C], off_34F3C4[dword_3ACD40]);
  result = swPtxBirth__Load_char_const__ptr__unsigned_char(v3, 1, 0);
  this[3] = result;
  return result;
}

```

### `mcCityModelInfo__Load_char_const__ptr__char_const__ptr`
- **MC2 Xbox VA:** `0x13C5E0..0x13c614` (64 B) | **MC3 Xbox VA:** `0x0A1E30` (71 B, delta: `+7 B`) | **MC3 PS2 VA:** `0x24C738`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_cbf51071f3a61a948e5236f10258f2b84905c5e2786b65ffae963786f8f29bc2`

```cpp
const char *__cdecl mcCityModelInfo__Load_char_const__ptr__char_const__ptr(int a1)
{
  const char *result; // eax

  switch ( a1 )
  {
    case 0:
      return "main";
    case 1:
      return "wind";
    case 2:
      return "refl";
  }
  result = "emissive";
  if ( a1 != 3 )
    return "***invalid***";
  return result;
}

```

### `mcAudioCityWalla__dtor_mcAudioCityWalla_void`
- **MC2 Xbox VA:** `0x1495C0..0x14961c` (96 B) | **MC3 Xbox VA:** `0x02B520` (220 B, delta: `+124 B`) | **MC3 PS2 VA:** `0x1BCC98`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_589ec1c1fc36219aa21ef3b71a164242f5c62ef8fd7fd28bdc821309da1fea2f`

```cpp
int __thiscall mcAudioCityWalla__dtor_mcAudioCityWalla_void(unsigned __int16 *this)
{
  int v2; // edi
  void (__thiscall ***v3)(_DWORD, int); // ecx
  void (__thiscall ***v4)(_DWORD, int); // ecx

  v2 = 0;
  if ( this[2] )
  {
    do
    {
      v3 = *(void (__thiscall ****)(_DWORD, int))(*(_DWORD *)this + 4 * v2);
      if ( v3 )
        (**v3)(v3, 1);
      *(_DWORD *)(*(_DWORD *)this + 4 * v2++) = 0;
    }
    while ( v2 < this[2] );
  }
  v4 = (void (__thiscall ***)(_DWORD, int))*((_DWORD *)this + 2);
  if ( v4 )
    (**v4)(v4, 1);
  sub_1D5260("walla");
  return _builtin_delete(*(_DWORD *)this);
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

### `mcProgressManager__CheckAndRequestPreCityMovie_int`
- **MC2 Xbox VA:** `0x14F830..0x14f8b2` (144 B) | **MC3 Xbox VA:** `0x277620` (320 B, delta: `+176 B`) | **MC3 PS2 VA:** `0x4C0C78`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_532de11553b2b4c741c21160a3bb053baf9488a01c7956b1ce14eead2c4bfe5f`

```cpp
char __thiscall mcProgressManager__CheckAndRequestPreCityMovie_int(int this)
{
  int v3; // eax

  if ( (unsigned __int8)mcProgressManager__AreMoviesDisabled_void() )
    return 0;
  v3 = dword_3504A0[1182 * *(_DWORD *)(this + 24)
                  + dword_34FDF4[1182 * *(_DWORD *)(this + 24)
                               + 33 * *(unsigned __int8 *)(this + 39)
                               + *(unsigned __int8 *)(*(unsigned __int8 *)(this + 39) + this + 28)]];
  if ( !v3 || *(_DWORD *)(this + 4) == 5 )
    return 0;
  sub_14E9F0(v3);
  sub_14E9D0(&byte_31FF74);
  sub_14E980(&byte_31FF74);
  *(_DWORD *)(this + 4) = 5;
  return 1;
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

### `mc__LoadCityData_char_const__ptr__bool`
- **MC2 Xbox VA:** `0x1510A0..0x15119e` (256 B) | **MC3 Xbox VA:** `0x26F700` (524 B, delta: `+268 B`) | **MC3 PS2 VA:** `0x4B77B0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_84161f47f90d1a34eb7a3860f3cb1b03fc3d44da1f332261cd5c7ccd890c3c72`

```cpp
int __cdecl mc__LoadCityData_char_const__ptr__bool(int a1)
{
  char v1; // bl
  int Data_datBinTokenizer__ref__phBound__FileVersion; // ebp
  int result; // eax
  int v4; // edi
  char v5; // [esp+10h] [ebp-144h]
  _DWORD v6[40]; // [esp+14h] [ebp-140h] BYREF
  _DWORD v7[40]; // [esp+B4h] [ebp-A0h] BYREF

  v1 = 0;
  Data_datBinTokenizer__ref__phBound__FileVersion = 0;
  v5 = 0;
  result = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(&dword_334798, a1, "loc", 0, 1);
  v4 = result;
  if ( result )
  {
    if ( (unsigned __int8)sub_20AAE0(&dword_334798, a1, "locinf") )
    {
      Data_datBinTokenizer__ref__phBound__FileVersion = phBound__LoadData_datBinTokenizer__ref__phBound__FileVersion(
                                                          &dword_334798,
                                                          a1,
                                                          "locinf",
                                                          0,
                                                          1);
      if ( Data_datBinTokenizer__ref__phBound__FileVersion )
      {
        v1 = 1;
        v5 = 1;
      }
    }
    v7[0] = &off_33ECE8;
    v7[39] = 0;
    datBaseTokenizer__Init_char_const__ptr__Stream__ptr(a1, v4);
    v6[0] = &off_33ECE8;
    v6[39] = 0;
    if ( v1 )
      datBaseTokenizer__Init_char_const__ptr__Stream__ptr("theInfo", Data_datBinTokenizer__ref__phBound__FileVersion);
    mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool((const char *)v7, (int)v6, v5);
    result = Stream__Close_void(v4);
    if ( v1 )
      return Stream__Close_void(Data_datBinTokenizer__ref__phBound__FileVersion);
  }
  return result;
}

```

### `mcUnlocking__IsCityUnlocked_int_const`
- **MC2 Xbox VA:** `0x153400..0x153440` (64 B) | **MC3 Xbox VA:** `0x289CC0` (32 B, delta: `-32 B`) | **MC3 PS2 VA:** `0x4D42B0`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_b1c50eba7d0a39885f417b5aedd0fbb5f67d1fbc6b9b60e1d2df9754cafb3a28`

```cpp
int __thiscall mcUnlocking__IsCityUnlocked_int_const(int *this, int a2, char a3)
{
  int v4; // esi

  v4 = 31;
  while ( a3 && (unsigned __int8)sub_150FE0(v4) != 1 || !mcUnlocking__IsItemUnlocked_int_int_const(this, v4) )
  {
    if ( --v4 < 0 )
      return 0;
  }
  return v4;
}

```

## 2. Full Symbol Equivalence Table (34 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x020780` | `0x02A2E0` | `0x1A8EC0` | `mcLayerCity__InitPhys_void` | 1104 | 256 | -848 | `seed` |
| `0x083650` | `0x26ED10` | `0x4B7600` | `mc__mcCityData__mcCityData_void` | 208 | 754 | +546 | `seed` |
| `0x100530` | `0x07FC00` | `0x22F070` | `mcTrainManager__LoadCityTrains_char_const__ptr` | 272 | 252 | -20 | `seed` |
| `0x120E00` | `0x03B0E0` | `0x1D2588` | `mcLightning__initStaticData_void` | 32 | 23 | -9 | `seed` |
| `0x121850` | `0x03BF80` | `0x5B9490` | `mcSpotlightTuneParams__GetTypeName_void` | 16 | 183 | +167 | `seed` |
| `0x121890` | `0x03C0C0` | `0x1D6650` | `mcSpotlightTuneParams__FileIO_datParser__ref` | 240 | 343 | +103 | `seed` |
| `0x12E1C0` | `0x092EF0` | `-` | `mcCullable__Enable_bool` | 64 | 84 | +20 | `prop_round_3` |
| `0x12EB30` | `0x09BE10` | `0x258E18` | `mcCity__InitGlobalLighting_char_const__ptr` | 426 | 914 | +488 | `seed` |
| `0x130A10` | `-` | `0x24CAC8` | `lightGlowCondition__Default_void` | 144 | 0 | +0 | `ps2_callgraph` |
| `0x130AC0` | `0x093340` | `0x5BB990` | `mcGlow__GetTypeName_void` | 16 | 230 | +214 | `seed` |
| `0x130AD0` | `0x093440` | `0x24CCE8` | `lightGlowCondition__FileIO_datParser__ref` | 208 | 195 | -13 | `seed` |
| `0x130BA0` | `-` | `0x24CE18` | `lightGlowCondition__setCurrentCondition_char_const__ptr__char_const__ptr` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x130C30` | `0x093510` | `0x5BB9C8` | `mcGlow__GetTypeName_void` | 9 | 6 | -3 | `seed` |
| `0x130EE0` | `0x093810` | `-` | `mcGlow__FileIO_datParser__ref` | 48 | 42 | -6 | `insn_signature` |
| `0x130F10` | `0x093840` | `0x24D8F8` | `mcGlow__FileIO_datParser__ref` | 576 | 1076 | +500 | `seed` |
| `0x131D00` | `0x0948F0` | `0x2507C0` | `glowInfo__glowInfo_void` | 224 | 303 | +79 | `seed` |
| `0x133BD0` | `0x097FF0` | `0x24CBC8` | `lightGlowCondition__lightGlowCondition_char_const__ptr__char_const__ptr` | 192 | 458 | +266 | `seed` |
| `0x133C90` | `0x0981C0` | `0x24CE60` | `mcGlow__mcGlow_void` | 944 | 492 | -452 | `seed` |
| `0x138860` | `0x3319B0` | `0x562450` | `mcCityEnvMap__LoadCondition_void` | 80 | 77 | -3 | `seed` |
| `0x13C5E0` | `0x0A1E30` | `0x24C738` | `mcCityModelInfo__Load_char_const__ptr__char_const__ptr` | 64 | 71 | +7 | `seed` |
| `0x13D7D0` | `0x3582B0` | `-` | `mcLightData__GetDirName_void` | 16 | 11 | -5 | `prop_round_2` |
| `0x13D7E0` | `0x358340` | `0x595B18` | `mcLightData__FileIO_datParser__ref` | 480 | 467 | -13 | `seed` |
| `0x1495C0` | `0x02B520` | `0x1BCC98` | `mcAudioCityWalla__dtor_mcAudioCityWalla_void` | 96 | 220 | +124 | `seed` |
| `0x14E790` | `0x26B050` | `0x4BE708` | `mcRaceConfig__SetCity_char_const__ptr` | 80 | 80 | +0 | `seed` |
| `0x14F830` | `0x277620` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreCityMovie_int` | 144 | 320 | +176 | `career_callgraph` |
| `0x14FF10` | `0x26DA10` | `0x4B7B20` | `mc__mcCityData__LookupHookmanRace_char_const__ptr__int` | 128 | 96 | -32 | `career_semantic_seed` |
| `0x1500D0` | `0x26F620` | `0x4B8DB0` | `mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref` | 656 | 219 | -437 | `seed` |
| `0x150360` | `0x26D340` | `0x4B9370` | `mc__LookupCity_char_const__ptr` | 80 | 76 | -4 | `seed` |
| `0x150AA0` | `0x26F010` | `0x4B7C38` | `mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref` | 1280 | 736 | -544 | `career_semantic_seed` |
| `0x151000` | `-` | `0x4B7900` | `mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x1510A0` | `0x26F700` | `0x4B77B0` | `mc__LoadCityData_char_const__ptr__bool` | 256 | 524 | +268 | `seed` |
| `0x153400` | `0x289CC0` | `0x4D42B0` | `mcUnlocking__IsCityUnlocked_int_const` | 64 | 32 | -32 | `career_callgraph` |
| `0x171DA0` | `0x092E00` | `0x24A3E0` | `mcCullable__Init_void` | 16 | 9 | -7 | `seed` |
| `0x303C50` | `0x413150` | `-` | `XDK::D3DDevice_SetRenderState_CullMode` | 240 | 104 | -136 | `insn_signature` |
