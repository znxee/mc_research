# REA Dossier: Career Mode, ProgressManager, Unlocking Rules, Hookmen & Roaming AI (`career_and_hookmen`)

- **REA Evidence ID:** `ev_017f81c6716558953f9339baf18348635afccfde056448a3094764cea9e821e7`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 63
- **Hex-Rays Decompiled Functions:** 55

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

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

### `mcHud__ShowFindHookmanPrompt_void`
- **MC2 Xbox VA:** `0x09AB90..0x9aded` (608 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_642ac27dcd1be2b9c03e24ce9376b4991f506d9dcd1cef5e826b85a4bbe2b1d2`

```cpp
char __thiscall mcHud__ShowFindHookmanPrompt_void(int this)
{
  int v2; // eax
  int *v3; // edi
  int v4; // esi
  int v5; // ebx
  int v6; // ebp
  int v7; // edi
  int v8; // eax
  int v9; // edi
  _DWORD *v10; // esi
  int v11; // ebx
  int i; // esi
  int *v14; // [esp+Ch] [ebp-8h]
  int *v15; // [esp+Ch] [ebp-8h]
  int v16; // [esp+10h] [ebp-4h]

  *(_BYTE *)(this + 43) = 0;
  sub_140C40(dword_3B6774);
  if ( !*(_BYTE *)(dword_3AD2F8 + 8) )
  {
    mcPlayerManager__SetInputEnable_bool_bool(1, 1);
    mcMenuControllerConfig__ResetPrevAxisValues_void(0);
  }
  v2 = *(_DWORD *)(dword_3ABF24 + 528);
  v3 = 0;
  if ( v2 )
    *(_BYTE *)(v2 + 16) = 1;
  if ( *(float *)(this + 12) < -3.0 )
    sub_140C30(dword_3B6774);
  *(_DWORD *)(this + 8) = 0;
  *(_DWORD *)(this + 12) = 0;
  v4 = 0;
  if ( dword_3ACD74 > 0 )
  {
    v3 = dword_3ACEA4;
    v14 = dword_3ACEA4;
    v5 = 8;
    v6 = *(_DWORD *)(dword_3813D0 + 4) + 280;
    do
    {
      if ( *(_DWORD *)(v5 + dword_37FFE4) )
      {
        if ( *(int *)(dword_3AD31C + 8) >= 0 )
        {
          sub_9B890(v4);
          *(_QWORD *)v6 = sub_1E3EC0(v4);
          *(_DWORD *)(v6 + 8) = sub_1E3EE0(v4);
        }
        if ( v3[7] != -1 )
        {
          if ( sub_153CC0(v3) )
            *(_BYTE *)(*(_DWORD *)(mcConfig__GetPlayer_int(v4) + 76) + 64) = 1;
          else
            *(_BYTE *)(*(_DWORD *)(mcConfig__GetPlayer_int(v4) + 76) + 64) = 0;
          if ( dword_3ACD50 == 12 )
          {
            mcConfig__GetPlayer_int(v4);
            sub_B8670(4);
          }
          else if ( dword_3AC6E0 == 2 && dword_3ACD50 == 1 )
          {
            if ( !*(_BYTE *)(*(_DWORD *)(dword_3813D0 + 4) + 4488) )
            {
              v7 = *(_DWORD *)(txtStringTable__Get_char_const__ptr("HM_FIND_HOOKMAN") + 8);
              mcConfig__GetPlayer_int(v4);
              sub_B9680(11, v7);
              mcConfig__GetPlayer_int(v4);
              sub_B8670(11);
              v3 = v14;
            }
          }
          else
          {
            mcConfig__GetPlayer_int(v4);
            sub_B8670(3);
          }
          if ( (*(int (__thiscall **)(_DWORD))(**(_DWORD **)(dword_3813D0 + 4) + 120))(*(_DWORD *)(dword_3813D0 + 4)) == 2
            && *(_DWORD *)(mcConfig__GetPlayer_int(v4) + 76) )
          {
            mcConfig__GetPlayer_int(v4);
            sub_83EA0(3, 2.0);
          }
        }
      }
      ++v4;
      v3 += 12;
      v5 += 4;
      v6 += 160;
      v14 = v3;
    }
    while ( v4 < dword_3ACD74 );
  }
  LOBYTE(v8) = byte_3ACE91;
  if ( byte_3ACE91 )
    LOBYTE(v8) = sub_9B890(dword_3ACE94);
  if ( dword_3AD324 )
  {
    v16 = v4;
    v15 = v3;
    v9 = dword_3AD324;
    if ( byte_3AD340 )
    {
      v10 = (_DWORD *)(dword_3AD324 + 24);
      v11 = 26;
      do
      {
        if ( *v10 )
          sub_155B00(*v10 + 16);
        ++v10;
        --v11;
      }
      while ( v11 );
    }
    v8 = *(_DWORD *)(v9 + 144);
    for ( i = 0; i < v8; ++i )
    {
      sub_154F20(*(_DWORD *)(*(_DWORD *)(v9 + 228) + 4 * i), v15, v16);
      v8 = *(_DWORD *)(v9 + 144);
    }
  }
  return v8;
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

### `mcProgressManager__GetHookmanState_int_int_const`
- **MC2 Xbox VA:** `0x14F140..0x14f188` (80 B) | **MC3 Xbox VA:** `0x293EA0` (96 B, delta: `+16 B`) | **MC3 PS2 VA:** `0x4D7A30`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_e766c97f17d0443be37b90bff2d3e2ad136232e99e4cfabcbe4ad1e2fd77c54a`

```cpp
bool __thiscall mcProgressManager__GetHookmanState_int_int_const(int this, int a2, char a3, char a4)
{
  if ( *(_DWORD *)(this + 4) == 1 || a2 >= 3 )
    return 0;
  return (*(unsigned __int16 *)(this + 2 * a2 + 72) & (1 << a3)) != 0 || !a4 && *(_BYTE *)(this + 40);
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

### `mcProgressManager__MarkHookmanBeaten_int_int`
- **MC2 Xbox VA:** `0x14F510..0x14f55d` (80 B) | **MC3 Xbox VA:** `0x293E40` (96 B, delta: `+16 B`) | **MC3 PS2 VA:** `0x4C8D98`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_855556581e6e8208976975701f1aa6fb3c5d3caa4a1c7f39c1ddbee59bf1b306`

```cpp
int __thiscall mcProgressManager__MarkHookmanBeaten_int_int(int this)
{
  int v2; // eax
  char **v3; // ecx
  int result; // eax

  v2 = *(unsigned __int8 *)(this + 39);
  v3 = &(&(&off_34FDE8)[1182 * *(_DWORD *)(this + 24)])[33 * v2];
  ++*(_BYTE *)(v2 + this + 28);
  result = *(unsigned __int8 *)(this + 39);
  *(_BYTE *)(this + 80) = 1;
  if ( *(unsigned __int8 *)(result + this + 28) < (int)v3[1] )
  {
    *(_BYTE *)(this + 16) = 0;
  }
  else
  {
    result = sub_14F190(*(_DWORD *)(this + 24), result);
    *(_BYTE *)(this + 16) = 1;
  }
  return result;
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

### `mcProgressManager__InitUnlockingRules_void`
- **MC2 Xbox VA:** `0x14FA80..0x14faba` (64 B) | **MC3 Xbox VA:** `0x28C3E0` (320 B, delta: `+256 B`) | **MC3 PS2 VA:** `0x4D3FD0`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_e3b613ef2e2446dd9e18c4df9318567944ed9c741b7618281ae14bb3f5f4010a`

```cpp
_DWORD *__thiscall mcProgressManager__InitUnlockingRules_void(_DWORD *this)
{
  *this = &off_33848C;
  this[1] = 0;
  *((_BYTE *)this + 80) = 0;
  sub_1539A0(this + 21);
  mcUnlocking__LoadRules_char_const__ptr(this, "tune/unlockingrules.csv");
  mcProgressManager__ResetCareerIteration_void(this);
  sub_14EF60();
  return this;
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

### `mcProgressManager__AdvanceHookmanProgress_void`
- **MC2 Xbox VA:** `0x14FC50..0x14fcb7` (112 B) | **MC3 Xbox VA:** `0x277E20` (192 B, delta: `+80 B`) | **MC3 PS2 VA:** `0x4C0400`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_05163cc47b992d88ee604a02bbcfd047f976cd1aad6bee0234435e57e8cf0240`

```cpp
char __thiscall mcProgressManager__AdvanceHookmanProgress_void(int this)
{
  int updated; // eax
  char result; // al
  int v4; // ecx
  _DWORD *v5; // ecx
  char v6; // al

  updated = mcProgressManager__UpdateHookmanRacesCompleted_int_int((void *)this);
  if ( updated == 3 )
    return sub_14EFB0(0);
  v4 = *(_DWORD *)(this + 24);
  if ( updated == v4 )
  {
    v6 = *(_BYTE *)(this + 39);
    if ( v6 != -1 && !mcProgressManager__GetHookmanState_int_int_const(this, v4, v6, 1) )
    {
      *(_DWORD *)(this + 4) = 4;
      return mcProgressManager__SetupNextCareerRace_void(this);
    }
LABEL_6:
    *(_DWORD *)(this + 4) = 3;
    return mcProgressManager__SetupNextCareerRace_void(this);
  }
  sub_14EF80(updated);
  result = mcProgressManager__CheckAndRequestPreRaceMovie_int_int(v5);
  if ( !result )
    goto LABEL_6;
  return result;
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

### `mcUnlocking__BuildCondition_char_const__ptr__char_const__ptr__uint__ref`
- **MC2 Xbox VA:** `0x1520A0..0x1521ee` (368 B) | **MC3 Xbox VA:** `0x28B850` (1072 B, delta: `+704 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_018792743809eb617c00fe7e622eda8e74e3bfe93ba70ce958c9d355e0272bc4`

```cpp
char __stdcall mcUnlocking__BuildCondition_char_const__ptr__char_const__ptr__uint__ref(_DWORD *a1, int a2, int a3)
{
  int v3; // edi
  int v4; // esi
  _DWORD *v5; // eax
  _DWORD *v6; // edi

  v3 = a2;
  v4 = 0;
  while ( strcasecmp(v3, *(&off_353F0C + v4)) )
  {
    if ( ++v4 >= 6 )
    {
      v5 = a1;
      *a1 = 0;
      v5[1] = 0;
      return (char)v5;
    }
  }
  v6 = a1;
  *a1 = v4;
  switch ( v4 )
  {
    case 0:
      LOBYTE(v5) = mc__LookupHookman_char_const__ptr__int__ref__int__ref(a3, &a1, (int)&a3);
      if ( (_BYTE)v5 )
        goto LABEL_12;
      goto LABEL_13;
    case 1:
    case 2:
      LOBYTE(v5) = mc__LookupRaceAcrossCities_char_const__ptr__int__ref__int__ref(a3, &a1, &a3);
      if ( (_BYTE)v5 )
        goto LABEL_12;
      goto LABEL_13;
    case 3:
      v5 = (_DWORD *)mc__LookupCity_char_const__ptr(a3);
      v6[1] = v5;
      return (char)v5;
    case 4:
      LOBYTE(v5) = mc__LookupHookman_char_const__ptr__int__ref__int__ref(a3, &a1, (int)&a3);
      if ( (_BYTE)v5 )
      {
LABEL_12:
        v5 = (_DWORD *)sub_151EB0(a1, a3);
        v6[1] = v5;
      }
      else
      {
LABEL_13:
        v6[1] = 0;
      }
      break;
    case 5:
      v5 = (_DWORD *)mc__LookupCar_char_const__ptr(a3);
      v6[1] = v5;
      break;
    default:
      strcmp("mcUnlocking::BuildCondition: unhandled condition type (switch statement)");
  }
  return (char)v5;
}

```

### `mcUnlocking__ConvertRuleIdsToNumerical_char_const__ptr__char_const__ptr__int__ref__int__ref`
- **MC2 Xbox VA:** `0x152210..0x1522f1` (272 B) | **MC3 Xbox VA:** `0x28B510` (832 B, delta: `+560 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_96b9a92b08c07c643c0cae57851b1f81ff4351c8e22ee8bbfdb386bb20c361e5`

```cpp
char __stdcall mcUnlocking__ConvertRuleIdsToNumerical_char_const__ptr__char_const__ptr__int__ref__int__ref(
        int a1,
        int a2,
        _DWORD *a3,
        _DWORD *a4)
{
  int v4; // edi
  int v5; // esi
  char result; // al
  int v7; // eax
  int v8; // eax
  int v9; // eax

  v4 = a1;
  v5 = 0;
  while ( strcasecmp(v4, *(&off_353F24 + v5)) )
  {
    if ( ++v5 >= 12 )
      return 0;
  }
  *a3 = v5;
  switch ( v5 )
  {
    case 0:
      v7 = mc__LookupCar_char_const__ptr(a2);
      *a4 = v7;
      return 1;
    case 1:
      if ( !(unsigned __int8)mc__LookupRaceAcrossCities_char_const__ptr__int__ref__int__ref(a2, &a1, &a2) )
        return 0;
      v8 = sub_151EB0(a1, a2);
      *a4 = v8;
      result = 1;
      break;
    case 2:
      v9 = mc__LookupCity_char_const__ptr(a2);
      *a4 = v9;
      return 1;
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
    case 10:
    case 11:
      *a4 = 0;
      return 1;
    default:
      strcmp("mcUnlocking::ConvertRuleIdsToNumerical: unhandled item type");
  }
  return result;
}

```

### `mcUnlocking__CheckRule_uint_const`
- **MC2 Xbox VA:** `0x152320..0x152458` (336 B) | **MC3 Xbox VA:** `0x28AE00` (416 B, delta: `+80 B`) | **MC3 PS2 VA:** `0x4D50B0`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_9c9dfcad08ca35892e2f9a0f8a10b08ea79b7bb069256b9f8dbcc2009bb01e42`

```cpp
bool __thiscall mcUnlocking__CheckRule_uint_const(int *this, int a2)
{
  int v3; // ebp
  bool i; // bl
  int v5; // edx
  int v6; // esi
  int v7; // eax
  int v8; // eax
  int v9; // eax
  int v11; // [esp+Ch] [ebp-18h] BYREF
  int v12; // [esp+10h] [ebp-14h] BYREF
  int v13; // [esp+14h] [ebp-10h] BYREF
  int v14; // [esp+18h] [ebp-Ch] BYREF
  int v15; // [esp+1Ch] [ebp-8h] BYREF
  int v16; // [esp+20h] [ebp-4h] BYREF

  v3 = 0;
  for ( i = 1; v3 < *(_DWORD *)(a2 + 8); ++v3 )
  {
    if ( !i )
      break;
    v5 = *(_DWORD *)(a2 + 12);
    v6 = *(_DWORD *)(v5 + 8 * v3);
    v7 = v5 + 8 * v3;
    switch ( v6 )
    {
      case 0:
        sub_151EC0(*(_DWORD *)(v7 + 4), &v12, &v11);
        i = mcProgressManager__IsRaceBeaten_int_int_const((_DWORD *)this[2], v12, v11);
        break;
      case 1:
      case 2:
        sub_151EC0(*(_DWORD *)(v7 + 4), &v14, &v13);
        i = mcProgressManager__GetHookmanState_int_int_const(this[2], v14, v13, v6 == 2);
        break;
      case 3:
        i = (unsigned __int8)sub_151EE0(*(_DWORD *)(v7 + 4), 0) != 0;
        break;
      case 4:
        sub_151EC0(*(_DWORD *)(v7 + 4), &v15, &v16);
        v8 = sub_1D8850(this[2]);
        if ( v8 != v15 || (v9 = sub_39260(this[2]), v9 != v16) )
          i = 0;
        break;
      case 5:
        i = (unsigned __int8)mcUnlocking__IsItemUnlocked_int_int_const(*(_DWORD *)(v7 + 4)) != 0;
        break;
      default:
        strcmp("mcUnlocking::CheckRule: unhandled condition type (switch statement)");
    }
  }
  return i;
}

```

### `mcUnlocking__EvaluateUnlockRule_int_int_const`
- **MC2 Xbox VA:** `0x1531B0..0x153249` (160 B) | **MC3 Xbox VA:** `0x28AFA0` (160 B, delta: `+0 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_8598ffa6a22c0e2bfc64bfb4007b0510424acb04681f5faa8adda945117b53ec`

```cpp
char __thiscall mcUnlocking__EvaluateUnlockRule_int_int_const(int *this, int a2, int a3)
{
  _DWORD *v4; // ebp
  char v5; // bl
  _DWORD *v6; // esi
  int v8; // [esp-14h] [ebp-38h]
  _DWORD *v9; // [esp+10h] [ebp-14h] BYREF
  _DWORD v10[4]; // [esp+14h] [ebp-10h] BYREF

  v4 = (_DWORD *)this[5];
  v5 = 0;
  v10[1] = a3;
  v10[0] = a2;
  v8 = this[4];
  v10[2] = 0;
  v10[3] = 0;
  mcPgBinaryRulesEvalBase__RuleOrGroup_const__ptr____lower_bound_mcPgBinaryRulesEvalBase__RuleOrGroup_const__ptr__mcPgBinaryRulesEvalBase__RuleOrGroup_mcPgBinaryRulesEvalBase__RuleOrGroup__Less_int_mcPgBinaryRulesEvalBase__RuleOrG__99c109ff21(
    &v9,
    v8,
    v4,
    v10);
  v6 = v9;
  if ( v9 == v4 || *v9 != a2 || v9[1] != a3 )
    return 1;
  do
  {
    if ( *v6 != a2 )
      break;
    if ( v6[1] != a3 )
      break;
    v5 |= mcUnlocking__CheckRule_uint_const(this, (int)v6);
    v6 += 4;
  }
  while ( v6 != (_DWORD *)this[5] );
  return v5;
}

```

### `mcUnlocking__IsItemUnlocked_int_int_const`
- **MC2 Xbox VA:** `0x153250..0x15326b` (32 B) | **MC3 Xbox VA:** `0x28B0A0` (96 B, delta: `+64 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_af3356649efe1c5a3e891c2244a40ebcfb8ddc0a121448dd2eaeb01a77e8928d`

```cpp
char __thiscall mcUnlocking__IsItemUnlocked_int_int_const(int *this, int a2)
{
  char result; // al

  result = 1;
  if ( byte_3AC6E7 != 1 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 0, a2);
  return result;
}

```

### `mcUnlocking__IsNitroUnlockedForPlayer_void_const`
- **MC2 Xbox VA:** `0x1532A0..0x1532b6` (32 B) | **MC3 Xbox VA:** `0x289E10` (32 B, delta: `+0 B`) | **MC3 PS2 VA:** `0x4D4710`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_b8d90a07c2eaa67237fa3024f48e7b2f4c98f539063c1c99e74c3f2e75cafc58`

```cpp
char __thiscall mcUnlocking__IsNitroUnlockedForPlayer_void_const(int *this)
{
  char result; // al

  result = 1;
  if ( byte_3AC6E9 != 1 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 3, 0);
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

### `mcUnlocking__IsBurnoutUnlocked_bool_const`
- **MC2 Xbox VA:** `0x153310..0x153360` (80 B) | **MC3 Xbox VA:** `0x289EF0` (16 B, delta: `-64 B`) | **MC3 PS2 VA:** `0x4D4790`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_fc8cfc128c0f203cd06d10f90816c77d484cd4f7ae53b25495ae568be9e4130f`

```cpp
char __thiscall mcUnlocking__IsBurnoutUnlocked_bool_const(int *this, char a2)
{
  if ( byte_3AC6E9 == 1 )
    return 1;
  if ( a2 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 5, 0);
  return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 5, 0)
      || mcUnlocking__EvaluateUnlockRule_int_int_const(this, 9, 0);
}

```

### `mcUnlocking__IsTwoWheelDrivingUnlocked_bool_const`
- **MC2 Xbox VA:** `0x153360..0x1533b0` (80 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `0x4D47D0`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_be4215d78a462b21c67a56ccbb359957cadb6fa04a1623d7701b2cc1be63fb3f`

```cpp
char __thiscall mcUnlocking__IsTwoWheelDrivingUnlocked_bool_const(int *this, char a2)
{
  if ( byte_3AC6E9 == 1 )
    return 1;
  if ( a2 )
    return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 6, 0);
  return mcUnlocking__EvaluateUnlockRule_int_int_const(this, 6, 0)
      || mcUnlocking__EvaluateUnlockRule_int_int_const(this, 10, 0);
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

### `mcUnlocking__IsHookmanUnlocked_int_int_const`
- **MC2 Xbox VA:** `0x153480..0x1534af` (48 B) | **MC3 Xbox VA:** `N/A` (null B, delta: `+null B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `career_callgraph` | **REA Function Evidence ID:** `ev_b8f9457ff508f7aab503ed3e4e7934655a9aa0d7753ddeb61088ae05e22e7037`

```cpp
char __thiscall mcUnlocking__IsHookmanUnlocked_int_int_const(int *this)
{
  int v2; // esi

  v2 = 0;
  while ( !(unsigned __int8)sub_1509C0(v2) || !mcUnlocking__IsItemUnlocked_int_int_const(this, v2) )
  {
    if ( ++v2 >= 32 )
      return 0;
  }
  return 1;
}

```

### `mcUnlocking__LoadRules_char_const__ptr`
- **MC2 Xbox VA:** `0x153A30..0x153bef` (448 B) | **MC3 Xbox VA:** `0x28C3E0` (320 B, delta: `-128 B`) | **MC3 PS2 VA:** `0x4D3FD0`
- **Match Method:** `career_semantic_seed` | **REA Function Evidence ID:** `ev_20aa1689520e240f9f8882949f05fd108e71ada0823930927191e6776f228f7b`

```cpp
char __thiscall mcUnlocking__LoadRules_char_const__ptr(int this, int a2, int a3)
{
  char result; // al
  int v5; // [esp+1Ch] [ebp-2Ch]
  _DWORD v6[5]; // [esp+30h] [ebp-18h] BYREF
  int v7; // [esp+44h] [ebp-4h]

  result = *(_BYTE *)(this + 4);
  if ( !result )
  {
    v6[0] = 22;
    v6[1] = 512;
    v6[3] = 0;
    v6[4] = 0;
    v7 = 0;
    v6[2] = sub_1789E0(88);
    if ( (unsigned __int8)sub_1E2FB0(&byte_31FF74, a3, 1, 6) )
    {
      v5 = v7;
      mcUnlocking__FinalizeAndSortRuleTables_void(
        *(_DWORD *)(this + 16),
        *(_DWORD *)(this + 20),
        (*(_DWORD *)(this + 20) - *(_DWORD *)(this + 16)) >> 4,
        0);
      *(_BYTE *)(this + 4) = 1;
      *(_DWORD *)(this + 8) = a2;
    }
    return sub_1E2F30(v6);
  }
  return result;
}

```

## 2. Full Symbol Equivalence Table (63 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x098186` | `0x16BFA0` | `0x35AA10` | `mcMenuRaceOver__PopulateMenu_int` | 550 | 2721 | +2171 | `seed` |
| `0x0983AC` | `0x16B51E` | `0x34FFD0` | `mcMenuRaceOver__HandleCareerAndCruiseSelection_int` | 2071 | 802 | -1269 | `career_semantic_seed` |
| `0x09AB90` | `-` | `-` | `mcHud__ShowFindHookmanPrompt_void` | 608 | null | +null | `career_semantic_seed` |
| `0x09DAE0` | `0x1A1760` | `0x3DDA08` | `mcRaceOver__CheckAndShowUnlockedCar_void` | 384 | 416 | +32 | `career_semantic_seed` |
| `0x09DC60` | `0x1A1760` | `0x3DDA08` | `mcRaceOver__CheckAndShowUnlockedAbilities_void` | 336 | 416 | +80 | `career_semantic_seed` |
| `0x0A26A0` | `0x1D3AE0` | `0x3D6ED8` | `mcRaceBase__LoadOpponents_datAsciiTokenizer__ref` | 1552 | 2116 | +564 | `seed` |
| `0x0A34F0` | `0x1D4F20` | `0x3D4A20` | `mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref` | 475 | 2832 | +2357 | `career_semantic_seed` |
| `0x0A43F0` | `0x1E06E0` | `0x3F4D60` | `mcRaceCheckpoint__PlayerFinished_int` | 1104 | 1585 | +481 | `seed` |
| `0x0ADDA0` | `0x1D7AB0` | `0x3E8248` | `mcRaceHookmen__PostLevelLoad_void` | 368 | 320 | -48 | `career_callgraph` |
| `0x0AE2C0` | `0x1D75A0` | `0x3E7660` | `mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int` | 576 | null | +null | `career_callgraph` |
| `0x0AE500` | `0x1D7780` | `0x3E7C58` | `mcRaceHookmen__PlayerFinishedFollow_void` | 160 | null | +null | `career_semantic_seed` |
| `0x0AEA80` | `0x1D6D70` | `0x3E8248` | `mcRaceHookmen__LoadAllHookmanSubRaces_void` | 368 | 560 | +192 | `career_callgraph` |
| `0x0AEEF0` | `0x1D7C00` | `0x3E7588` | `mcRaceHookmen__Update_void` | 1024 | null | +null | `career_callgraph` |
| `0x0AF2F0` | `0x1D6D70` | `0x3E8710` | `mcRaceHookmen__Load_char_const__ptr__char_const__ptr` | 176 | 560 | +384 | `career_semantic_seed` |
| `0x0C7370` | `0x1EB540` | `0x3FDE28` | `aiBrainHookman__PreUpdate_void` | 142 | 1232 | +1090 | `career_callgraph` |
| `0x0C73FE` | `0x1EBA20` | `0x3FDDC8` | `aiBrainHookman__Update_void` | 930 | 1056 | +126 | `career_callgraph` |
| `0x0C77A0` | `0x1EC140` | `0x3FE580` | `aiBrainHookman__RestartCruise_void` | 304 | 272 | -32 | `career_semantic_seed` |
| `0x0C7940` | `0x1EC250` | `0x3FE810` | `aiBrainHookman__IsEngagedAndReadyForRace_void_const` | 48 | 464 | +416 | `career_callgraph` |
| `0x14E6A0` | `0x26AF20` | `0x4BE508` | `mcRaceConfig__SetTOD_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E6F0` | `0x26AF70` | `0x4BE598` | `mcRaceConfig__SetRaceType_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E740` | `0x26AFC0` | `0x4BE628` | `mcRaceConfig__SetWeather_char_const__ptr` | 80 | 71 | -9 | `seed` |
| `0x14E790` | `0x26B050` | `0x4BE708` | `mcRaceConfig__SetCity_char_const__ptr` | 80 | 80 | +0 | `seed` |
| `0x14EB40` | `0x26B770` | `0x4BE1C8` | `mcRaceConfig__LoadInfo_datAsciiTokenizer__ref` | 320 | 358 | +38 | `seed` |
| `0x14ED80` | `0x26BAB0` | `0x4BE0D0` | `mcRaceConfig__LoadRaceInfo_void` | 208 | 205 | -3 | `seed` |
| `0x14EFF0` | `0x27D350` | `0x4C8990` | `mcProgressManager__IsRaceBeaten_int_int_const` | 96 | 240 | +144 | `career_callgraph` |
| `0x14F140` | `0x293EA0` | `0x4D7A30` | `mcProgressManager__GetHookmanState_int_int_const` | 80 | 96 | +16 | `career_callgraph` |
| `0x14F300` | `0x277530` | `0x4C0880` | `mcProgressManager__SetupCareerCruise_int` | 528 | 240 | -288 | `career_semantic_seed` |
| `0x14F510` | `0x293E40` | `0x4C8D98` | `mcProgressManager__MarkHookmanBeaten_int_int` | 80 | 96 | +16 | `career_callgraph` |
| `0x14F560` | `0x276FC0` | `0x4C0060` | `mcProgressManager__SelectHookmanRaceFromFollow_int_int` | 80 | 160 | +80 | `career_callgraph` |
| `0x14F5F0` | `0x277350` | `0x4C02C0` | `mcProgressManager__UpdateHookmanRacesCompleted_int_int` | 112 | 240 | +128 | `career_callgraph` |
| `0x14F670` | `-` | `-` | `mcProgressManager__AreMoviesDisabled_void` | 32 | null | +null | `career_callgraph` |
| `0x14F730` | `-` | `0x4BF9E0` | `mcProgressManager__ResetCareerIteration_void` | 64 | null | +null | `career_callgraph` |
| `0x14F770` | `0x277CA0` | `0x4C0708` | `mcProgressManager__MarkRaceAsBeaten_int_int` | 192 | 384 | +192 | `career_semantic_seed` |
| `0x14F830` | `0x277620` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreCityMovie_int` | 144 | 320 | +176 | `career_callgraph` |
| `0x14F8C0` | `0x277760` | `0x4C00C8` | `mcProgressManager__CheckAndRequestPostRaceMovie_int_int` | 304 | 464 | +160 | `career_callgraph` |
| `0x14F9F0` | `0x2774B0` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreRaceMovie_int_int` | 144 | 128 | -16 | `career_callgraph` |
| `0x14FA80` | `0x28C3E0` | `0x4D3FD0` | `mcProgressManager__InitUnlockingRules_void` | 64 | 320 | +256 | `career_semantic_seed` |
| `0x14FAF0` | `0x278270` | `0x4BFBD8` | `mcProgressManager__SetupNextCareerRace_void` | 352 | 272 | -80 | `career_semantic_seed` |
| `0x14FC50` | `0x277E20` | `0x4C0400` | `mcProgressManager__AdvanceHookmanProgress_void` | 112 | 192 | +80 | `career_callgraph` |
| `0x14FCC0` | `0x277EE0` | `0x4BFDB0` | `mcProgressManager__ReportRaceResult_int` | 304 | 512 | +208 | `career_semantic_seed` |
| `0x14FF10` | `0x26DA10` | `0x4B7B20` | `mc__mcCityData__LookupHookmanRace_char_const__ptr__int` | 128 | 96 | -32 | `career_semantic_seed` |
| `0x1500D0` | `0x26F620` | `0x4B8DB0` | `mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref` | 656 | 219 | -437 | `seed` |
| `0x1504F0` | `-` | `0x4B96F0` | `mc__LookupHookman_char_const__ptr__int__ref__int__ref` | 80 | null | +null | `career_callgraph` |
| `0x150AA0` | `0x26F010` | `0x4B7C38` | `mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref` | 1280 | 736 | -544 | `career_semantic_seed` |
| `0x151000` | `-` | `0x4B7900` | `mc__LoadCityData_datAsciiTokenizer__ref__datAsciiTokenizer__ref__bool` | 160 | 0 | +0 | `ps2_callgraph` |
| `0x1510A0` | `0x26F700` | `0x4B77B0` | `mc__LoadCityData_char_const__ptr__bool` | 256 | 524 | +268 | `seed` |
| `0x1520A0` | `0x28B850` | `-` | `mcUnlocking__BuildCondition_char_const__ptr__char_const__ptr__uint__ref` | 368 | 1072 | +704 | `career_semantic_seed` |
| `0x152210` | `0x28B510` | `-` | `mcUnlocking__ConvertRuleIdsToNumerical_char_const__ptr__char_const__ptr__int__ref__int__ref` | 272 | 832 | +560 | `career_semantic_seed` |
| `0x152320` | `0x28AE00` | `0x4D50B0` | `mcUnlocking__CheckRule_uint_const` | 336 | 416 | +80 | `career_semantic_seed` |
| `0x1531B0` | `0x28AFA0` | `-` | `mcUnlocking__EvaluateUnlockRule_int_int_const` | 160 | 160 | +0 | `career_callgraph` |
| `0x153250` | `0x28B0A0` | `-` | `mcUnlocking__IsItemUnlocked_int_int_const` | 32 | 96 | +64 | `career_callgraph` |
| `0x153270` | `0x28B100` | `-` | `mcUnlocking__PackItemKey_int_int` | 48 | 80 | +32 | `career_callgraph` |
| `0x1532A0` | `0x289E10` | `0x4D4710` | `mcUnlocking__IsNitroUnlockedForPlayer_void_const` | 32 | 32 | +0 | `career_callgraph` |
| `0x1532C0` | `0x289D80` | `0x4D4750` | `mcUnlocking__IsSlipstreamTurboUnlocked_bool_const` | 80 | 80 | +0 | `career_callgraph` |
| `0x153310` | `0x289EF0` | `0x4D4790` | `mcUnlocking__IsBurnoutUnlocked_bool_const` | 80 | 16 | -64 | `career_callgraph` |
| `0x153360` | `-` | `0x4D47D0` | `mcUnlocking__IsTwoWheelDrivingUnlocked_bool_const` | 80 | null | +null | `career_callgraph` |
| `0x1533B0` | `-` | `0x4D4810` | `mcUnlocking__IsInAirControlUnlocked_bool_const` | 80 | null | +null | `career_callgraph` |
| `0x153400` | `0x289CC0` | `0x4D42B0` | `mcUnlocking__IsCityUnlocked_int_const` | 64 | 32 | -32 | `career_callgraph` |
| `0x153440` | `-` | `0x4D4550` | `mcUnlocking__IsVehicleUnlocked_int_const` | 64 | null | +null | `career_callgraph` |
| `0x153480` | `-` | `-` | `mcUnlocking__IsHookmanUnlocked_int_int_const` | 48 | null | +null | `career_callgraph` |
| `0x153570` | `0x28BC80` | `-` | `mcUnlocking__FinalizeAndSortRuleTables_void` | 288 | 352 | +64 | `career_callgraph` |
| `0x153A30` | `0x28C3E0` | `0x4D3FD0` | `mcUnlocking__LoadRules_char_const__ptr` | 448 | 320 | -128 | `career_semantic_seed` |
| `0x1E7100` | `0x289E10` | `-` | `mcPgUnlockingRulesEval__IsNitroUnlockedForPlayer_void_const` | 464 | 24 | -440 | `insn_signature` |
