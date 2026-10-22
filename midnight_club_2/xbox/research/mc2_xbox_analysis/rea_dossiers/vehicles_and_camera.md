# REA Dossier: Vehicles, Tuning, Particles, Cameras & Replay (`vehicles_and_camera`)

- **REA Evidence ID:** `ev_43c124fbc5a665ad12c9338918e3ecbd2ca71d45af8d1e78889ef47d230d0cec`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 69
- **Hex-Rays Decompiled Functions:** 13

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

### `mcPlayerCamera__InitCameras_char_const__ptr`
- **MC2 Xbox VA:** `0x084070..0x84608` (1440 B) | **MC3 Xbox VA:** `0x2C5710` (790 B, delta: `-650 B`) | **MC3 PS2 VA:** `0x514670`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_793955f1a6ba28493673f1c4c9406690f6b0368a79487d4e7a315925c1b9b360`

```cpp
_DWORD *__thiscall mcPlayerCamera__InitCameras_char_const__ptr(_DWORD *this, int a2, int a3, const char *a4)
{
  int v5; // eax
  int v6; // eax
  int v7; // eax
  int v8; // eax
  _DWORD *v9; // edi
  int v10; // eax
  _DWORD *v11; // eax
  int v12; // eax
  _DWORD *v13; // eax
  int v14; // eax
  _DWORD *v15; // eax
  int v16; // eax
  _DWORD *v17; // eax
  int v18; // eax
  int v19; // eax
  int v20; // eax
  int v21; // eax
  int v22; // eax
  int v23; // eax
  int v24; // eax
  int v25; // edx
  int v26; // ebp
  int v27; // eax
  int v28; // ebp
  int v29; // eax
  int v30; // ebp
  int v31; // eax
  int v32; // ebp
  int v33; // eax
  int v34; // ebp
  int v35; // eax
  int v36; // ebp
  int v37; // eax
  int v38; // ebp
  int v39; // eax
  int v40; // ebp
  int v41; // eax
  int v42; // eax
  int v43; // eax
  int v44; // eax
  int v45; // eax
  _BYTE v47[64]; // [esp+8h] [ebp-40h] BYREF

  this[1] = a3;
  this[17] = a2;
  *this = &off_32BD0C;
  v5 = dword_3ACEC4[12 * a2];
  if ( v5 >= 0 )
    this[14] = sub_1D8B00(4 * v5 + 3853608);
  sub_153CE0(&dword_3ACEA4[12 * this[17]]);
  this[2] = 0;
  v6 = _builtin_new(336);
  if ( v6 )
    v7 = sub_86620(v6);
  else
    v7 = 0;
  *(_DWORD *)(v7 + 320) = 65551;
  this[6] = v7;
  v8 = _builtin_new(568);
  if ( v8 )
    v9 = (_DWORD *)sub_85DB0(v8);
  else
    v9 = 0;
  v9[132] = 65551;
  v9[34] = 0;
  v9[35] = 1070638039;
  v9[36] = 0;
  v9[66] = 0;
  v9[67] = 1050253722;
  v9[68] = 1082549862;
  v9[137] = 1061997773;
  v9[138] = 1079613850;
  v9[139] = 1085276160;
  sub_860E0(v9);
  this[7] = v9;
  v10 = _builtin_new(568);
  if ( v10 )
    v11 = (_DWORD *)sub_85DB0(v10);
  else
    v11 = 0;
  v11[132] = 65551;
  v11[34] = 0;
  v11[35] = 1069044204;
  v11[36] = 0;
  v11[66] = 0;
  v11[67] = 1061997773;
  v11[68] = 1082549862;
  v11[137] = 1063675494;
  v11[138] = 1079613850;
  v11[139] = 1087373312;
  this[8] = v11;
  v12 = _builtin_new(568);
  if ( v12 )
    v13 = (_DWORD *)sub_85DB0(v12);
  else
    v13 = 0;
  v13[132] = 65551;
  v13[34] = 0;
  v13[35] = 1070638039;
  v13[36] = 0;
  v13[66] = 0;
  v13[67] = 1069547520;
  v13[68] = 1084227584;
  v13[137] = 1066192077;
  v13[138] = 1082130432;
  v13[139] = 1090519040;
  this[9] = v13;
  v14 = _builtin_new(568);
  if ( v14 )
    v15 = (_DWORD *)sub_85DB0(v14);
  else
    v15 = 0;
  v15[132] = 65551;
  v15[34] = 0;
  v15[35] = 1072902963;
  v15[36] = 0;
  v15[66] = 0;
  v15[67] = 1072064102;
  v15[68] = 1085485875;
  v15[73] = 1082130432;
  v15[41] = 1097859072;
  v15[74] = 1088421888;
  v15[75] = 0x40000000;
  v15[76] = 1094713344;
  v15[137] = 1065353216;
  v15[138] = 1084647014;
  v15[139] = 1093140480;
  this[10] = v15;
  v16 = _builtin_new(532);
  if ( v16 )
    v17 = (_DWORD *)sub_17B300(v16);
  else
    v17 = 0;
  v17[132] = 65551;
  v17[34] = 0;
  v17[35] = 1071644672;
  v17[36] = 0;
  v17[66] = 0;
  v17[67] = 1060320051;
  v17[68] = -1058013184;
  v17[38] = 0;
  v17[74] = 1101004800;
  v17[73] = 0;
  v17[41] = 1097859072;
  v17[39] = 1106247680;
  v17[49] = 1088421888;
  v17[48] = 1090519040;
  v17[31] = 1112014848;
  this[11] = v17;
  v18 = _builtin_new(180);
  if ( v18 )
    v19 = sub_852F0(v18);
  else
    v19 = 0;
  this[12] = v19;
  *(_DWORD *)(v19 + 156) = 65551;
  v20 = _builtin_new(852);
  if ( v20 )
    v21 = sub_85070(v20);
  else
    v21 = 0;
  this[15] = v21;
  *(_DWORD *)(v21 + 528) = 65551;
  *((_BYTE *)this + 64) = 0;
  v22 = _builtin_new(252);
  if ( v22 )
    v23 = sub_85B00(v22);
  else
    v23 = 0;
  this[13] = v23;
  this[4] = 0;
  this[3] = 0;
  this[5] = 0;
  v24 = sub_153CC0(&dword_3ACEA4[12 * a2]);
  v25 = this[1];
  *((_BYTE *)this + 64) = v24 != 0;
  v26 = *(_DWORD *)(*(_DWORD *)(v25 + 16) + 72);
  v27 = strlen(v47, 64, "%s_POV", a4);
  sub_17B1D0(v26, v27);
  v28 = *(_DWORD *)(*(_DWORD *)(this[1] + 16) + 72);
  v29 = strlen(v47, 64, "%s_chase1", a4);
  sub_17B1D0(v28, v29);
  *(_DWORD *)(this[7] + 244) = 0;
  v30 = *(_DWORD *)(*(_DWORD *)(this[1] + 16) + 72);
  v31 = strlen(v47, 64, "%s_chase2", a4);
  sub_17B1D0(v30, v31);
  *(_DWORD *)(this[8] + 244) = 0;
  v32 = *(_DWORD *)(*(_DWORD *)(this[1] + 16) + 72);
  v33 = strlen(v47, 64, "%s_chase3", a4);
  sub_17B1D0(v32, v33);
  *(_DWORD *)(this[9] + 244) = 0;
  v34 = *(_DWORD *)(*(_DWORD *)(this[1] + 16) + 72);
  v35 = strlen(v47, 64, "%s_chase4", a4);
  sub_17B1D0(v34, v35);
  *(_DWORD *)(this[10] + 244) = 0;
  v36 = *(_DWORD *)(this[1] + 16);
  v37 = strlen(v47, 64, "%s_reverse", a4);
  sub_17B1D0(*(_DWORD *)(v36 + 72), v37);
  v38 = *(_DWORD *)(this[1] + 16);
  v39 = strlen(v47, 64, "%s_wipeout", a4);
  sub_853A0(*(_DWORD *)(v38 + 72), v39);
  v40 = *(_DWORD *)(this[1] + 16);
  v41 = strlen(v47, 64, "%s_cinematic", a4);
  sub_17B1D0(*(_DWORD *)(v40 + 72), v41);
  v42 = _builtin_new(72);
  if ( v42 )
    v43 = sub_17D790(v42);
  else
    v43 = 0;
  this[3] = v43;
  v44 = _builtin_new(160);
  if ( v44 )
    v45 = sub_17DC30(v44);
  else
    v45 = 0;
  this[4] = v45;
  sub_17D800(v45);
  sub_17D810(this[this[14] + 6]);
  if ( this[13] )
    sub_85C10(this[17], *(_DWORD *)(this[1] + 16), this[3], this[6]);
  sub_838F0(this);
  return this;
}

```

### `mcReplayCamera__Init_int_mcCar__ptr__camViewCS__ptr__vehPovCS__ptr`
- **MC2 Xbox VA:** `0x085C9E..0x85d7e` (274 B) | **MC3 Xbox VA:** `0x2CDFB0` (436 B, delta: `+162 B`) | **MC3 PS2 VA:** `0x51BA90`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_b0fecdb1051f7f045ac26095a75644f6a9a1693fe459f52150f238667ae5a645`

```cpp
// positive sp value has been detected, the output may be wrong!
int __userpurge mcReplayCamera__Init_int_mcCar__ptr__camViewCS__ptr__vehPovCS__ptr@<eax>(
        _DWORD *a1@<eax>,
        int a2@<edi>,
        _DWORD *a3@<esi>,
        int a4,
        int a5,
        char a6,
        int a7)
{
  int v7; // eax
  _DWORD *v8; // ebx
  int v9; // eax
  int v11; // [esp-40h] [ebp-40h] BYREF

  *a1 = a2;
  a1[5] = a2;
  a1[4] = a2;
  a1[3] = a2;
  a1[8] = a2;
  a1[7] = a2;
  a1[6] = a2;
  a1[11] = a2;
  a1[10] = a2;
  a1[9] = a2;
  *(_DWORD *)(a3[46] + 108) = a1;
  v7 = _builtin_new(568);
  if ( v7 == a2 )
    v8 = 0;
  else
    v8 = (_DWORD *)sub_85DB0(v7);
  v8[132] = 17;
  v8[34] = a2;
  v8[35] = 1069547520;
  v8[36] = a2;
  v8[66] = a2;
  v8[67] = 1045220557;
  v8[68] = 1080033280;
  sub_860E0(v8);
  v9 = strlen(&v11, 64, "%s_chase1", "replay");
  sub_17B1D0(*(_DWORD *)(a3[41] + 72), v9);
  v8[61] = a2;
  a3[61] = v8;
  a3[39] = 1106247680;
  a3[40] = 1112014848;
  return ((int (__thiscall *)(_DWORD *))sub_85860)(a3);
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

### `mcCarDamageTune__GetTypeName_void`
- **MC2 Xbox VA:** `0x0DBAB0..0xdbab6` (16 B) | **MC3 Xbox VA:** `0x101A60` (23 B, delta: `+7 B`) | **MC3 PS2 VA:** `0x5BE228`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_b4cdf3ef95c1d4eec0a60beb225917093535914c64732667a6eaf183db6af9eb`

```cpp
const char *mcCarDamageTune__GetTypeName_void()
{
  return "vehDamage";
}

```

### `mcCarModelTune__GetTypeName_void`
- **MC2 Xbox VA:** `0x0E0A60..0xe0a66` (16 B) | **MC3 Xbox VA:** `0x0FB4E0` (93 B, delta: `+77 B`) | **MC3 PS2 VA:** `0x5BE788`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_b7cffb09985ebc6a599d9303909a20eb22248b226a1380aa917e01e52290e999`

```cpp
const char *mcCarModelTune__GetTypeName_void()
{
  return "vehModel";
}

```

### `mcCarParticlesManager__mcCarParticlesManager_void`
- **MC2 Xbox VA:** `0x0E4F60..0xe5679` (1824 B) | **MC3 Xbox VA:** `0x113B50` (704 B, delta: `-1120 B`) | **MC3 PS2 VA:** `0x2ED2A0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_f951c3c03bbca555214d5b1ff980df63f7581753104ed247c6bc4c1b99f4803a`

```cpp
int __thiscall mcCarParticlesManager__mcCarParticlesManager_void(
        _DWORD *this,
        const char *a2,
        int a3,
        int a4,
        int a5,
        int a6,
        int a7)
{
  int v8; // eax
  int v9; // ecx
  char v10; // al
  int v11; // eax
  int v12; // eax
  int v13; // eax
  int v14; // eax
  _DWORD *v15; // eax
  _DWORD *v16; // eax
  int v17; // ecx
  _DWORD *v18; // eax
  int v19; // edx
  _DWORD *v20; // eax
  int v21; // ecx
  _BYTE v23[48]; // [esp+8h] [ebp-70h] BYREF
  _BYTE v24[64]; // [esp+38h] [ebp-40h] BYREF

  parFileIO__SetName_char_const__ptr(a2);
  mcCullable__Init_void(this + 3);
  v8 = sub_FC180("model", a2, a5, a6, a7);
  this[5] = v8;
  this[9] = a3;
  this[29] = a4;
  v9 = *(_DWORD *)(v8 + 14652);
  if ( v9 )
  {
    dword_356C3C = (int)nullsub_6 + 214013 * dword_356C3C;
    this[25] = (int)(HIWORD(dword_356C3C) & 0x7FFF) % (v9 - 1) + 1;
  }
  if ( dword_386114 )
  {
    this[3098] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/rainParticle", 128);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C2C, 1, 1);
    this[3097] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/mistParticle", 256);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C30, 1, 1);
    this[3095] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/shallowWaterParticle", 256);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C34, 1, 1);
    this[3096] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/deepWaterParticle", 128);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C38, 1, 1);
    this[3099] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/engineFire", 32);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C54, 1, 1);
    this[3100] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/engineSmoke", 96);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C3C, 1, 1);
    this[3107] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/engineSparks", 32);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C60, 1, 1);
    this[3101] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/explosionFire", 32);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C58, 1, 1);
    this[3102] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/explosionSmoke", 96);
    swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C40, 1, 1);
    if ( *((_BYTE *)this + 9948) )
    {
      this[3103] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/missileFire", 32);
      swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C5C, 1, 1);
      this[3104] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/missileSmoke", 96);
      swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C44, 1, 1);
      this[3105] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/bulletSmoke", 32);
      swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C48, 1, 1);
      this[3106] = swPtxBirthTabled__LoadWithHash_char__ptr("tune/vehicle/bulletFlash", 16);
      swPtxBirth__SetTexture_gfxTexture__ptr__unsigned_char_unsigned_char(dword_382C4C, 1, 1);
    }
    sub_DD260(this);
  }
  v10 = *((_BYTE *)this + 9948);
  *((_BYTE *)this + 12688) = 0;
  if ( v10 )
  {
    if ( _builtin_new(104) )
      v11 = sndControl3d__sndControl3d_char_const__ptr("HUD:cheat_missle");
    else
      v11 = 0;
    this[3170] = v11;
    sndControl__sndControl_char_const__ptr(*(_DWORD *)(dword_3B6774 + 24));
  }
  else
  {
    this[3170] = 0;
  }
  if ( (_BYTE)a5 )
  {
    if ( _builtin_new(104) )
      v12 = sndControl3d__sndControl3d_char_const__ptr("trunk_slam:trunk_slam");
    else
      v12 = 0;
    this[3171] = v12;
    sndControl__sndControl_char_const__ptr(*(_DWORD *)(dword_3B6774 + 24));
  }
  else
  {
    this[3171] = 0;
  }
  if ( (unsigned __int8)sub_1769B0(a2, "hlight0") )
  {
    strlen(v24, 64, "%s_hlight0_h", a2);
    sub_176990(v23, a2, "hlight0");
    sub_DBB50(v23);
    *(_DWORD *)(this[2422] + 12) = gfxGetModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int(
                                     "model",
                                     "vp_shared_headlight",
                                     0,
                                     274);
  }
  if ( (unsigned __int8)sub_1769B0(a2, "hlight1") )
  {
    strlen(v24, 64, "%s_hlight1_h", a2);
    sub_176990(v23, a2, "hlight1");
    sub_DBB50(v23);
    *(_DWORD *)(this[2423] + 12) = gfxGetModelPrefix_char_const__ptr__char_const__ptr__int_unsigned_int(
                                     "model",
                                     "vp_shared_headlight",
                                     0,
                                     274);
  }
  v13 = _builtin_new(908);
  if ( v13 )
    v14 = sub_12A680(v13);
  else
    v14 = 0;
  this[28] = v14;
  if ( v14 )
  {
    sub_129C60(this[29], a2);
    if ( (unsigned __int8)sub_1769B0(a2, "flame0") )
    {
      sub_176990(v24, a2, "flame0");
      sub_129D20(v24, *(_DWORD *)(this[5] + 7584));
    }
    if ( (unsigned __int8)sub_1769B0(a2, "flame1") )
    {
      sub_176990(v24, a2, "flame1");
      sub_129D20(v24, *(_DWORD *)(this[5] + 7588));
    }
  }
  v15 = (_DWORD *)this[5];
  this[3112] = v15[2310];
  this[3113] = v15[2311];
  this[3114] = v15[2312];
  this[3115] = v15[2313];
  this[3116] = v15[2314];
  this[3117] = v15[2315];
  this[3118] = v15[2316];
  this[3119] = v15[2317];
  this[3120] = v15[2318];
  this[3121] = v15[2319];
  this[3122] = v15[2320];
  this[3123] = v15[2321];
  v16 = (_DWORD *)this[5];
  this[3124] = v16[2322];
  this[3125] = v16[2323];
  this[3126] = v16[2324];
  this[3127] = v16[2325];
  this[3128] = v16[2326];
  this[3129] = v16[2327];
  v17 = v16[2328];
  v16 += 2322;
  this[3130] = v17;
  this[3131] = v16[7];
  this[3132] = v16[8];
  this[3133] = v16[9];
  this[3134] = v16[10];
  this[3135] = v16[11];
  v18 = (_DWORD *)this[5];
  this[3136] = v18[2334];
  v19 = v18[2335];
  v18 += 2334;
  this[3137] = v19;
  this[3138] = v18[2];
  this[3139] = v18[3];
  this[3140] = v18[4];
  this[3141] = v18[5];
  this[3142] = v18[6];
  this[3143] = v18[7];
  this[3144] = v18[8];
  this[3145] = v18[9];
  this[3146] = v18[10];
  this[3147] = v18[11];
  v20 = (_DWORD *)this[5];
  v21 = v20[2346];
  v20 += 2346;
  this[3148] = v21;
  this[3149] = v20[1];
  this[3150] = v20[2];
  this[3151] = v20[3];
  this[3152] = v20[4];
  this[3153] = v20[5];
  this[3154] = v20[6];
  this[3155] = v20[7];
  this[3156] = v20[8];
  this[3157] = v20[9];
  this[3158] = v20[10];
  this[3159] = v20[11];
  return (*(int (__thiscall **)(_DWORD *))(*this + 8))(this);
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

### `mcProgressManager__SetupCareerCruise_int`
- **MC2 Xbox VA:** `0x14F300..0x14f501` (528 B) | **MC3 Xbox VA:** `0x277530` (240 B, delta: `-288 B`) | **MC3 PS2 VA:** `0x4C0880`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_8202790824fe3e60c8ece821fe7b6a6df16fd71f0022ef1adb9aa7cf81737c6b`

```cpp
int __thiscall mcProgressManager__SetupCareerCruise_int(int this, int a2)
{
  int v4; // esi
  int v5; // ecx
  char v7; // [esp+13h] [ebp-9h]
  int v8; // [esp+14h] [ebp-8h]
  char v9; // [esp+18h] [ebp-4h]
  char **v10; // [esp+20h] [ebp+4h]

  v4 = 0;
  v8 = 0;
  v7 = 1;
  v9 = -1;
  dword_3AC968 = a2;
  dword_3AC980 = 1;
  sub_14E980(&byte_31FF74);
  dword_3AC96C = 1;
  dword_3ACAD4 = dword_3ACAD8;
  dword_3AC970 = 0;
  *(_DWORD *)(this + 8) = a2;
  if ( dword_34FDB8[1182 * a2] <= 0 )
    goto LABEL_11;
  v10 = &(&off_34FDE8)[1182 * a2];
  do
  {
    if ( !mcProgressManager__GetHookmanState_int_int_const(this, a2, v4, 1)
      && (unsigned __int8)mcUnlocking__PackItemKey_int_int(a2, v4) == 1 )
    {
      v5 = (int)v10[2];
      if ( v5 < 0 && (int)v10[*(unsigned __int8 *)(v4 + this + 28) + 18] < 0 )
      {
        v7 = 0;
        v9 = v4;
      }
      sub_14E880(v8++, v4, v5, v10[*(unsigned __int8 *)(v4 + this + 28) + 18]);
    }
    ++v4;
    v10 += 33;
  }
  while ( v4 < dword_34FDB8[1182 * a2] );
  if ( !v8 )
  {
LABEL_11:
    *(_DWORD *)(this + 4) = 6;
    return mcProgressManager__SetupNextCareerRace_void(this);
  }
  if ( !v7 )
  {
    *(_BYTE *)(this + 39) = v9;
    *(_BYTE *)(this + 80) = 1;
    *(_DWORD *)(this + 4) = 4;
    return mcProgressManager__SetupNextCareerRace_void(this);
  }
  dword_3ACCA0 = v8;
  *(_DWORD *)(this + 12) = -1;
  *(_DWORD *)(this + 4) = 3;
  if ( dword_3ACCA0 == 1 )
  {
    if ( !dword_3AC968 )
    {
      if ( !dword_3ACCA4 && dword_3ACCD0 == -1 && dword_3ACCFC >= 0 )
        return sub_14E9D0("moses_first_follow_ls");
      return sub_14E9D0("lamauro_Arcade_Cruise_ls");
    }
  }
  else if ( !dword_3AC968 )
  {
    return sub_14E9D0("lamauro_Arcade_Cruise_ls");
  }
  if ( dword_3AC968 == 1 )
    return sub_14E9D0("paris_Arcade_Cruise_ls");
  if ( dword_3AC968 == 2 )
    return sub_14E9D0("tokyoarcade_Arcade_Cruise_ls");
  return sub_14E9D0(&byte_31FF74);
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

### `mcUnlocking__IsVehicleUnlocked_int_const`
- **MC2 Xbox VA:** `0x153440..0x15347d` (64 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x4D4550`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_3f57e5cb89e1e1364745ccae5e98f2d642f2439c2f0d4dbeeef597bcbc2277cf`

```cpp
int __thiscall mcUnlocking__IsVehicleUnlocked_int_const(int *this)
{
  int v1; // edi
  int v2; // ebx
  int i; // esi
  __int64 v5; // rax

  v1 = 0;
  v2 = 0;
  for ( i = 0; i < 32; ++i )
  {
    if ( mcUnlocking__IsItemUnlocked_int_int_const(this, i) )
    {
      v5 = sub_20F2F0(i, 0);
      v1 |= v5;
      v2 |= HIDWORD(v5);
    }
  }
  return v1;
}

```

## 2. Full Symbol Equivalence Table (69 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x017BE0` | `0x01DAA0` | `0x5B8A58` | `mcLoadScreenTransition__GetTypeName_void` | 16 | 97 | +81 | `seed` |
| `0x017C20` | `0x01DB60` | `0x1A4030` | `mcLoadScreenTransition__FileIO_datParser__ref` | 128 | 81 | -47 | `seed` |
| `0x01A960` | `-` | `0x1C1CC0` | `mcExplosionParticles__mcExplosionParticles_void` | 16 | 0 | +0 | `ps2_callgraph` |
| `0x01ABE0` | `0x023E90` | `0x1BB230` | `mcReplayManager__DrawReplayControls_void` | 428 | 410 | -18 | `seed` |
| `0x04D9B0` | `0x33D600` | `0x578538` | `mcFeMemCard__FileIO_datParser__ref` | 144 | 106 | -38 | `seed` |
| `0x04DA70` | `0x33D790` | `0x575860` | `mcFeMemCard__ShowAccessWarning_mcFeMemCard__AccessType` | 176 | 200 | +24 | `seed` |
| `0x04E040` | `0x33EC10` | `0x574828` | `mcFeMemCard__CreateWidgets_void` | 448 | 571 | +123 | `seed` |
| `0x04E322` | `0x33E1C0` | `0x575F88` | `mcFeMemCard__UpdateSavegameSelectList_void` | 158 | 2367 | +2209 | `seed` |
| `0x04F647` | `0x33F3F0` | `0x577D20` | `mcFeMemCard__HandleMemcardError_mcFeMemCard__Operation_int` | 537 | 564 | +27 | `seed` |
| `0x07FC40` | `0x2C9960` | `0x5E8110` | `mcFeMemCard__AllWidgets__AllWidgets_void` | 16 | 6 | -10 | `seed` |
| `0x084070` | `0x2C5710` | `0x514670` | `mcPlayerCamera__InitCameras_char_const__ptr` | 1440 | 790 | -650 | `seed` |
| `0x085C9E` | `0x2CDFB0` | `0x51BA90` | `mcReplayCamera__Init_int_mcCar__ptr__camViewCS__ptr__vehPovCS__ptr` | 274 | 436 | +162 | `seed` |
| `0x087E20` | `0x032440` | `-` | `mcParticleFogTune__GetDirName_void` | 48 | 33 | -15 | `insn_signature` |
| `0x091F90` | `0x0EEDF0` | `0x2BF3A8` | `mcArchetypeBreak__LoadData_datAsciiTokenizer__ref__phBound__ptr` | 160 | 199 | +39 | `seed` |
| `0x0983AC` | `0x16B51E` | `0x34FFD0` | `mcMenuRaceOver__HandleCareerAndCruiseSelection_int` | 2071 | 802 | -1269 | `career_semantic_seed` |
| `0x09C3F0` | `0x1CAEF0` | `0x3D7960` | `mcRaceBase__LoadOpponentCarAiInfo_int_datAsciiTokenizer__ref` | 336 | 331 | -5 | `seed` |
| `0x09DAE0` | `0x1A1760` | `0x3DDA08` | `mcRaceOver__CheckAndShowUnlockedCar_void` | 384 | 416 | +32 | `career_semantic_seed` |
| `0x0B9740` | `0x0B4B50` | `0x5BCE50` | `hudSplashTranslatedText__GetTypeName_void` | 16 | 110 | +94 | `seed` |
| `0x0BEB00` | `0x0D5550` | `0x275260` | `hudDamage__Init_int_hudHud__ptr__hudHud__Anchors` | 160 | 181 | +21 | `seed` |
| `0x0BEF40` | `0x0D59B0` | `0x275EF0` | `hudDamage__SharedData__TextureData__FileIO_datParser__ref__char_const__ptr` | 320 | 310 | -10 | `seed` |
| `0x0BF410` | `0x0D5EB0` | `-` | `hudDamage__SharedData__FileIO_datParser__ref` | 160 | 199 | +39 | `seed` |
| `0x0BF4C0` | `0x0D5F80` | `0x275DE0` | `hudDamage__SharedData__FileIO_datParser__ref` | 224 | 143 | -81 | `seed` |
| `0x0DBAB0` | `0x101A60` | `0x5BE228` | `mcCarDamageTune__GetTypeName_void` | 16 | 23 | +7 | `seed` |
| `0x0E0A60` | `0x0FB4E0` | `0x5BE788` | `mcCarModelTune__GetTypeName_void` | 16 | 93 | +77 | `seed` |
| `0x0E4F60` | `0x113B50` | `0x2ED2A0` | `mcCarParticlesManager__mcCarParticlesManager_void` | 1824 | 704 | -1120 | `seed` |
| `0x0E9EC0` | `0x129330` | `0x30CBD0` | `mcCarModEngine__FileIO_datParser__ref` | 560 | 233 | -327 | `seed` |
| `0x0EC070` | `0x33CC00` | `0x56F1A0` | `vehEngineSoundData__FileIO_datParser__ref` | 240 | 288 | +48 | `seed` |
| `0x0ECC00` | `0x33BFC0` | `0x570D70` | `vehWheelSoundData__FileIO_datParser__ref` | 352 | 691 | +339 | `seed` |
| `0x0ED3C0` | `0x33D2A0` | `0x5713D0` | `vehWindNoiseSoundData__FileIO_datParser__ref` | 112 | 113 | +1 | `seed` |
| `0x0F2E60` | `0x12A130` | `0x30EB80` | `mcCarStuckTune__FileIO_datParser__ref` | 48 | 499 | +451 | `seed` |
| `0x0F7800` | `0x10FC30` | `0x2F5B28` | `mcPowerUpTypeQuadDamage__mcPowerUpTypeQuadDamage_void` | 32 | 34 | +2 | `seed` |
| `0x0FC420` | `0x12EEB0` | `0x30C338` | `mcCarAeroTune__FileIO_datParser__ref` | 160 | 145 | -15 | `seed` |
| `0x0FC610` | `0x12EBE0` | `0x30C8E8` | `mcCarFluidTune__FileIO_datParser__ref` | 144 | 123 | -21 | `seed` |
| `0x1049C0` | `0x077AE0` | `0x22D0C0` | `aiAmbientVehicle__CreateSmoke_void` | 1427 | 1312 | -115 | `seed` |
| `0x10A510` | `0x07B720` | `0x21F778` | `aiAmbientType__SetVehicleClass_void` | 192 | 102 | -90 | `seed` |
| `0x14F300` | `0x277530` | `0x4C0880` | `mcProgressManager__SetupCareerCruise_int` | 528 | 240 | -288 | `career_semantic_seed` |
| `0x14F730` | `-` | `0x4BF9E0` | `mcProgressManager__ResetCareerIteration_void` | 64 | null | +null | `career_callgraph` |
| `0x14FAF0` | `0x278270` | `0x4BFBD8` | `mcProgressManager__SetupNextCareerRace_void` | 352 | 272 | -80 | `career_semantic_seed` |
| `0x1503B0` | `-` | `-` | `mc__LookupCar_char_const__ptr` | 80 | null | +null | `career_semantic_seed` |
| `0x153440` | `-` | `0x4D4550` | `mcUnlocking__IsVehicleUnlocked_int_const` | 64 | null | +null | `career_callgraph` |
| `0x166C30` | `0x2078B0` | `-` | `uiTranslatedText__uiTranslatedText_char_const__ptr__char_const__ptr__int_int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 80 | 80 | +0 | `prop_round_1` |
| `0x169590` | `0x0AD3B0` | `0x267788` | `vehTransTune__FileIO_datParser__ref` | 288 | 230 | -58 | `seed` |
| `0x16ADE0` | `0x0A2620` | `-` | `vehChassis__MakeSuspensions_char_const__ptr` | 79 | 384 | +305 | `prop_round_1` |
| `0x16B240` | `0x0A2CA0` | `0x25E5B8` | `vehChassis__MakeAxles_char_const__ptr` | 192 | 259 | +67 | `seed` |
| `0x16B370` | `0x0A2DB0` | `0x25E6F8` | `vehChassis__MakeSuspensions_char_const__ptr` | 720 | 833 | +113 | `seed` |
| `0x16B800` | `0x0A2460` | `-` | `vehChassis__Reset_void` | 1360 | 350 | -1010 | `prop_round_1` |
| `0x16C5A0` | `0x0A3CA0` | `0x2613C0` | `vehChassisTune__Lerp_float_vehChassisTune_const__ptr__vehChassisTune_const__ptr` | 576 | 471 | -105 | `seed` |
| `0x16C800` | `0x0A28B0` | `0x25E0D0` | `vehChassis__MakeWheels_char_const__ptr__int` | 864 | 825 | -39 | `seed` |
| `0x16CC90` | `0x35E220` | `0x59C558` | `vehDriver__Init_vehSim__ptr__vehDriverTune_const__ptr__Matrix34_const__ptr` | 224 | 257 | +33 | `seed` |
| `0x16D180` | `0x35E350` | `0x59CC98` | `vehDriverTune__GetDirName_void` | 352 | 299 | -53 | `seed` |
| `0x1703D0` | `0x0A6DA0` | `0x26B0C8` | `vehWheelTune__FileIO_datParser__ref` | 496 | 563 | +67 | `seed` |
| `0x171610` | `0x0ACA70` | `0x263258` | `vehEngineTune__FileIO_datParser__ref` | 224 | 230 | +6 | `seed` |
| `0x1721D0` | `0x35EC80` | `0x59F848` | `vehStuckTune__FileIO_datParser__ref` | 160 | 145 | -15 | `seed` |
| `0x1728E0` | `0x3606F0` | `0x59D7C0` | `vehGyroTune__FileIO_datParser__ref` | 224 | 211 | -13 | `seed` |
| `0x172F80` | `0x0AC0A0` | `0x26BCB0` | `vehAeroTune__FileIO_datParser__ref` | 128 | 123 | -5 | `seed` |
| `0x175F80` | `0x0ADEE0` | `0x262510` | `vehDrivetrainTune__FileIO_datParser__ref` | 80 | 76 | -4 | `seed` |
| `0x1763D0` | `0x0AE920` | `0x26C530` | `vehAxleTune__FileIO_datParser__ref` | 64 | 54 | -10 | `seed` |
| `0x176CB0` | `0x3305F0` | `-` | `vehSim__SetResetPos_Vector3_const__ref` | 32 | 29 | -3 | `insn_signature` |
| `0x178D60` | `-` | `0x4514E8` | `fxParticles__Reset_void` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x179300` | `-` | `0x452300` | `fxMeshCardInfo__fxMeshCardInfo_void` | 16 | 0 | +0 | `ps2_callgraph` |
| `0x1796E0` | `0x21E190` | `0x4511A8` | `fxParticles__fxParticles_void` | 176 | 222 | +46 | `seed` |
| `0x179800` | `0x21E2E0` | `0x4513B8` | `fxParticles__Init_int_int_int_int_fxMeshCardVertex__ptr` | 96 | 91 | -5 | `seed` |
| `0x179860` | `0x21E340` | `0x451500` | `fxParticles__SetTexture_gfxTexture__ptr__bool` | 64 | 59 | -5 | `seed` |
| `0x17A5A0` | `-` | `0x452408` | `fxParticleMgr__Add_fxParticles__ptr` | 32 | 0 | +0 | `ps2_callgraph` |
| `0x17AEC0` | `0x21FBB0` | `0x450678` | `fxBirthRule__InitSpark_fxSparkInfo__ptr__fxParticles__ref__int` | 704 | 700 | -4 | `seed` |
| `0x17C070` | `0x357410` | `0x594B40` | `vehTrackCS__FileIO_datParser__ref` | 752 | 790 | +38 | `seed` |
| `0x17CFD0` | `0x357FF0` | `0x5916D0` | `vehPovCS__FileIO_datParser__ref` | 208 | 194 | -14 | `seed` |
| `0x1EC700` | `0x2D3DA0` | `-` | `gfxState::SetCamera` | 32 | 221 | +189 | `prop_round_2` |
| `0x207040` | `0x20E150` | `-` | `mcMemCard__GetInfoStart_int_int__ptr__char_const__ptr__int__ptr__int__ptr__bool` | 16 | 5 | -11 | `prop_round_1` |
