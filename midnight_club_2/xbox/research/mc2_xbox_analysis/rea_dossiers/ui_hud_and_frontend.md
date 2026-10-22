# REA Dossier: HUD Map, Menus, Frontend, Movie & Network UI (`ui_hud_and_frontend`)

- **REA Evidence ID:** `ev_5508a3d78a7e51d0f4ed54c314c96e7c85aea5dcefb2585fda48017a22acc5ee`
- **MC2 Xbox Target SHA-256:** `5ae26db3e2dfafedae205e882dc710ef6a257a44fbad777de7562a61e39d9c4d`
- **Matched Symbols in Subsystem:** 244
- **Hex-Rays Decompiled Functions:** 19

## 1. Decompiled Functions (MC2 Xbox x86 -> C++)

### `hudMap__Init_int_hudHud__ptr__hudHud__Anchors`
- **MC2 Xbox VA:** `0x022290..0x22371` (68 B) | **MC3 Xbox VA:** `0x0BDA40` (287 B, delta: `+219 B`) | **MC3 PS2 VA:** `0x27D150`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_706aad34b041ce86f7313a05b328fc1089f650e3e65814ec783243f2bd64d6b9`

```cpp
char __thiscall hudMap__Init_int_hudHud__ptr__hudHud__Anchors(int this)
{
  int char_const__ptr__unsigned_char; // eax

  *(_BYTE *)(this + 921) = 1;
  *(_DWORD *)(this + 780) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_border", 0, 0);
  *(_DWORD *)(this + 784) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_checkpoint", 0, 0);
  *(_DWORD *)(this + 788) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_select", 0, 0);
  *(_DWORD *)(this + 792) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_arrowup", 0, 0);
  *(_DWORD *)(this + 796) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_arrowdown", 0, 0);
  *(_DWORD *)(this + 800) = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_dot", 0, 0);
  LOBYTE(char_const__ptr__unsigned_char) = byte_376670;
  if ( byte_376670 )
  {
    if ( byte_376670 == 1 )
    {
      char_const__ptr__unsigned_char = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_mapparis", 0, 0);
      *(_DWORD *)(this + 776) = char_const__ptr__unsigned_char;
    }
    else if ( byte_376670 == 2 )
    {
      char_const__ptr__unsigned_char = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_maptokyo", 0, 0);
      *(_DWORD *)(this + 776) = char_const__ptr__unsigned_char;
    }
  }
  else
  {
    char_const__ptr__unsigned_char = swPtxBirth__Load_char_const__ptr__unsigned_char("ui_re_mapla", 0, 0);
    *(_DWORD *)(this + 776) = char_const__ptr__unsigned_char;
  }
  return char_const__ptr__unsigned_char;
}

```

### `mcMoviePlayer__Play_char_const__ptr`
- **MC2 Xbox VA:** `0x037EC0..0x38072` (431 B) | **MC3 Xbox VA:** `0x15AA30` (594 B, delta: `+163 B`) | **MC3 PS2 VA:** `0x3647A8`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_9aff58503ceff9973b93c4273851d79507ff2ad771a114bcc9405b49ebd7945f`

```cpp
char __thiscall mcMoviePlayer__Play_char_const__ptr(int this, const char *a2)
{
  _BYTE *v3; // eax
  char *v4; // edi
  char result; // al
  int v7; // eax
  char *v8; // [esp-4h] [ebp-188h]
  int v9; // [esp+10h] [ebp-174h] BYREF
  char v10[31]; // [esp+14h] [ebp-170h] BYREF
  char v11; // [esp+33h] [ebp-151h] BYREF
  char v12[80]; // [esp+34h] [ebp-150h] BYREF
  _BYTE v13[256]; // [esp+84h] [ebp-100h] BYREF

  if ( (unsigned __int8)sub_208060("moviepath", 0, &v9) )
    sprintf(v13, "%s%s", v9, a2);
  else
    sprintf(v13, "%svideo/%s", "D:\\", a2);
  strcpy(v10, a2);
  v3 = (_BYTE *)strrchr(v10, 46);
  if ( v3 )
    *v3 = 0;
  if ( !strcmp(v10, "sd_logo") )
  {
    *(_DWORD *)(this + 16) = 1063675494;
  }
  else if ( !strcmp(v10, "mc2intro") || !strcmp(v10, "rockstar") )
  {
    *(_DWORD *)(this + 16) = 1060320051;
  }
  else
  {
    *(_DWORD *)(this + 16) = 1056964608;
  }
  v8 = (char *)a2;
  if ( !byte_3AC778 )
  {
    strlen(v12, 80, "%s", a2);
    if ( strstr(v12, ".txt") || strstr(v12, ".pss") )
      v10[strlen(v12) + 28] = 0;
    v4 = &v11;
    while ( *++v4 )
      ;
    strcpy(v4, "_tut");
    v8 = v12;
  }
  *(_BYTE *)(this + 24) = txtMovieSubtitles__SetupSubtitles_char_const__ptr(v8);
  result = sub_1E9E30(v13, 0);
  if ( result )
  {
    if ( *(_BYTE *)(this + 25) )
      v7 = sub_21940(this + 8);
    else
      v7 = 0;
    *(_DWORD *)(this + 36) = v7;
    result = 1;
    *(_BYTE *)(this + 27) = 1;
    *(_DWORD *)(this + 32) = 0;
  }
  return result;
}

```

### `mcMenuShell__ChangeState_MenuStates`
- **MC2 Xbox VA:** `0x038FF0..0x3901d` (48 B) | **MC3 Xbox VA:** `0x162590` (45 B, delta: `-3 B`) | **MC3 PS2 VA:** `N/A`
- **Match Method:** `insn_signature` | **REA Function Evidence ID:** `ev_248533a34d2a4809d4989b7b55ba37b360398de5f20fc929a917979e938e1594`

```cpp
int *__thiscall mcMenuShell__ChangeState_MenuStates(int *this, int *a2)
{
  int v2; // esi
  int v4; // ecx

  v2 = *a2;
  v4 = *this;
  if ( *a2 != v4 )
  {
    if ( v4 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v4 + 12))(v4);
    *this = v2;
    if ( v2 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v2 + 4))(v2);
  }
  return this;
}

```

### `mcMenuGeneral__PopulateMenu_void`
- **MC2 Xbox VA:** `0x03F000..0x3f358` (851 B) | **MC3 Xbox VA:** `0x18E2C0` (872 B, delta: `+21 B`) | **MC3 PS2 VA:** `0x3488E0`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_e9952826e915787776bc0f7b3024f0a4c960b902995565664e93ba8386e2392a`

```cpp
int __userpurge mcMenuGeneral__PopulateMenu_void@<eax>(int a1@<ebp>, int a2@<edi>, int a3@<esi>, int a4)
{
  int v4; // ebx
  int v5; // ecx
  int v6; // ebx
  int v7; // ecx
  int v8; // ebx
  int v9; // ecx
  int v11; // [esp-4h] [ebp-4h]
  int v12; // [esp-4h] [ebp-4h]
  int v13; // [esp-4h] [ebp-4h]
  int v14; // [esp-4h] [ebp-4h]

  v11 = *(_DWORD *)(a3 + 4 * a2 + 728);
  if ( v11 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v11 + 4))(v11, v11);
  sub_64970(v11);
  sub_64600(sub_38CC0, a1);
  sub_65D00("CM_Icon_Mode_Transparency_On", "ui_icon_on", 0, 0, -1, 1);
  sub_65D00("CM_Icon_Mode_Transparency_Off", "ui_icon_off", 1, 0, -1, 1);
  if ( _builtin_new(84) )
    v4 = sub_65B00(400, 61, 0);
  else
    v4 = 0;
  v5 = *(_DWORD *)(a3 + 4 * a2 + 648);
  if ( v4 != v5 )
  {
    if ( v5 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v5 + 8))(v5);
    *(_DWORD *)(a3 + 4 * a2 + 648) = v4;
    if ( v4 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v4 + 4))(v4);
  }
  v12 = *(_DWORD *)(a3 + 4 * a2 + 712);
  if ( v12 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v12 + 4))(v12, v12);
  sub_64970(v12);
  sub_64600(sub_38CC0, a1);
  sub_65D00("CM_Cinematic_Camera_On", "ui_icon_on", 1, 0, -1, 1);
  sub_65D00("CM_Cinematic_Camera_Off", "ui_icon_off", 0, 0, -1, 1);
  if ( _builtin_new(84) )
    v6 = sub_65B00(400, 64, 0);
  else
    v6 = 0;
  v7 = *(_DWORD *)(a3 + 4 * a2 + 680);
  if ( v6 != v7 )
  {
    if ( v7 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v7 + 8))(v7);
    *(_DWORD *)(a3 + 4 * a2 + 680) = v6;
    if ( v6 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v6 + 4))(v6);
  }
  v13 = *(_DWORD *)(a3 + 4 * a2 + 648);
  if ( v13 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v13 + 4))(v13, v13);
  sub_64970(v13);
  sub_64600(sub_38CC0, a1);
  sub_65D00("CM_Default_Camera_POV", "ui_icon_camera_pov", 0, 0, 0, 1);
  sub_65D00("CM_Default_Camera_1", "ui_icon_camera_1", 1, 0, 1, 1);
  sub_65D00("CM_Default_Camera_2", "ui_icon_camera_2", 2, 0, 2, 1);
  sub_65D00("CM_Default_Camera_3", "ui_icon_camera_3", 3, 0, 3, 1);
  sub_65D00("CM_Default_Camera_4", "ui_icon_camera_4", 4, 0, 4, 1);
  if ( _builtin_new(84) )
    v8 = sub_65B00(400, 63, 0);
  else
    v8 = 0;
  v9 = *(_DWORD *)(a3 + 4 * a2 + 696);
  if ( v8 != v9 )
  {
    if ( v9 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v9 + 8))(v9);
    *(_DWORD *)(a3 + 4 * a2 + 696) = v8;
    if ( v8 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v8 + 4))(v8);
  }
  v14 = *(_DWORD *)(a3 + 4 * a2 + 680);
  if ( v14 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v14 + 4))(v14, v14);
  sub_64970(v14);
  sub_64600(sub_38CC0, a1);
  sub_65D00("CM_Mini_Map_Rotation_On", "ui_icon_on", 0, 0, -1, 1);
  sub_65D00("CM_Mini_Map_Rotation_Off", "ui_icon_off", 1, 0, -1, 1);
  if ( !_builtin_new(84) )
    JUMPOUT(0x3F363);
  return mcMenuHud__PopulateMenu_void(a4);
}

```

### `mcMenuHud__PopulateMenu_void`
- **MC2 Xbox VA:** `0x03F358..0x3fc99` (1099 B) | **MC3 Xbox VA:** `0x18E940` (993 B, delta: `-106 B`) | **MC3 PS2 VA:** `0x352528`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_6b65f1477c7d047f4c00dc3721618a952fd5a1862f56484a223f4487ea0f44c8`

```cpp
// positive sp value has been detected, the output may be wrong!
int __userpurge mcMenuHud__PopulateMenu_void@<eax>(int a1@<ebp>, int a2@<edi>, int a3@<esi>, int a4)
{
  int v4; // ebx
  int v5; // ecx
  int v6; // ebx
  int v7; // ecx
  int v8; // ebx
  int v9; // ecx
  int v10; // ebx
  int v11; // ecx
  int v12; // ebx
  int v13; // ecx
  int v14; // ebx
  const char *v15; // eax
  int v16; // edi
  int v17; // edi
  int v18; // ecx
  int v19; // edi
  int v20; // ecx
  int v21; // edi
  int v22; // ecx
  int v23; // esi
  int result; // eax
  int v25; // [esp-114h] [ebp-114h]
  int v26; // [esp-114h] [ebp-114h]
  int v27; // [esp-114h] [ebp-114h]
  int v28; // [esp-114h] [ebp-114h]
  int v29; // [esp-114h] [ebp-114h]
  int v30; // [esp-114h] [ebp-114h]
  int v31; // [esp-114h] [ebp-114h]
  int v32; // [esp-114h] [ebp-114h]
  int v33; // [esp-114h] [ebp-114h]
  int v34; // [esp-114h] [ebp-114h]
  int v35; // [esp-110h] [ebp-110h]
  int v36; // [esp-110h] [ebp-110h]
  int v37; // [esp-110h] [ebp-110h]
  int v38; // [esp-110h] [ebp-110h]
  int v39; // [esp-110h] [ebp-110h]
  int v40; // [esp-110h] [ebp-110h]
  int v41; // [esp-110h] [ebp-110h]
  int v42; // [esp-110h] [ebp-110h]
  int v43; // [esp-110h] [ebp-110h]
  int v44; // [esp-110h] [ebp-110h]
  int v45; // [esp-10Ch] [ebp-10Ch]
  int v46; // [esp-10Ch] [ebp-10Ch]
  int v47; // [esp-10Ch] [ebp-10Ch]
  char v48; // [esp-10Ch] [ebp-10Ch]
  int v49; // [esp-10Ch] [ebp-10Ch]
  char v50; // [esp-10Ch] [ebp-10Ch]
  char v51; // [esp-10Ch] [ebp-10Ch]
  char v52; // [esp-10Ch] [ebp-10Ch]
  char v53; // [esp-10Ch] [ebp-10Ch]
  char v54; // [esp-10Ch] [ebp-10Ch]
  char v55; // [esp-10Ch] [ebp-10Ch]
  char v56; // [esp-10Ch] [ebp-10Ch]
  char v57; // [esp-10Ch] [ebp-10Ch]
  int v58; // [esp-10Ch] [ebp-10Ch]
  int v59; // [esp-F8h] [ebp-F8h]
  int v60; // [esp-F4h] [ebp-F4h]
  _BYTE v61[20]; // [esp-F0h] [ebp-F0h] BYREF
  _BYTE v62[220]; // [esp-DCh] [ebp-DCh] BYREF

  v8 = sub_65B00(v25, v35, v45);
  v9 = *(_DWORD *)(a3 + 4 * a2 + 664);
  if ( v8 != v9 )
  {
    if ( v9 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v9 + 8))(v9);
    *(_DWORD *)(a3 + 4 * a2 + 664) = v8;
    if ( v8 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v8 + 4))(v8);
  }
  v46 = *(_DWORD *)(a3 + 4 * a2 + 696);
  if ( v46 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v46 + 4))(v46, v46);
  sub_64970(v46);
  sub_64600(sub_38CC0, a1);
  sub_65D00("CM_Mirror_On", "ui_icon_on", 0, 0, -1, 1);
  sub_65D00("CM_Mirror_Off", "ui_icon_off", 1, 0, -1, 1);
  sub_65D00("CM_Mirror_Auto", "ui_icon_auto", 2, 0, -1, 1);
  if ( _builtin_new(84) )
    v10 = sub_65B00(400, 59, 0);
  else
    v10 = 0;
  v11 = *(_DWORD *)(a3 + 4 * a2 + 632);
  if ( v10 != v11 )
  {
    if ( v11 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v11 + 8))(v11);
    *(_DWORD *)(a3 + 4 * a2 + 632) = v10;
    if ( v10 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v10 + 4))(v10);
  }
  sub_64600(sub_38CC0, a1);
  sub_645C0(sub_3D850, a1);
  sub_65D00("CM_Controller_Vibration_On", "ui_icon_on", 1, 0, -1, 1);
  sub_65D00("CM_Controller_Vibration_Off", "ui_icon_off", 0, 0, -1, 1);
  if ( _builtin_new(84) )
    v12 = sub_65B00(400, 59, 0);
  else
    v12 = 0;
  v13 = *(_DWORD *)(a3 + 4 * a2 + 616);
  if ( v12 != v13 )
  {
    if ( v13 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v13 + 8))(v13);
    *(_DWORD *)(a3 + 4 * a2 + 616) = v12;
    if ( v12 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v12 + 4))(v12);
  }
  v47 = *(_DWORD *)(a3 + 4 * a2 + 632);
  if ( v47 )
    (*(void (__thiscall **)(int, int))(*(_DWORD *)v47 + 4))(v47, v47);
  sub_64970(v47);
  sub_64600(sub_38C60, a1);
  sub_645C0(sub_3D7E0, a1);
  sub_65D00("CM_Controller_1", "ui_icon_a", 0, 0, -1, 1);
  sub_65D00("CM_Controller_2", "ui_icon_b", 1, 0, -1, 1);
  sub_65D00("CM_Controller_3", "ui_icon_c", 2, 0, -1, 1);
  sub_65D00("CM_Controller_4", "ui_icon_d", 3, 0, -1, 1);
  sub_65D00("CM_Controller_5", "ui_icon_e", 4, 0, -1, 1);
  sub_65D00("CM_Controller_6", "ui_icon_f", 5, 0, -1, 1);
  v14 = a2 + 1;
  strlen(v62, 20, "CM_Player_%d", a2 + 1);
  v15 = &byte_31FF74;
  if ( a2 )
    v15 = (const char *)&word_321FF4;
  strlen(v61, 20, "ui_icon_%dplayer%s", a2 + 1, v15);
  v48 = 1;
  v36 = -1;
  v26 = *(_DWORD *)(a3 + 4 * a2 + 616);
  if ( v26 )
    (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v26 + 4))(v26, v26, -1, 1);
  sub_65D00(v62, v61, a2, v26, v36, v48);
  v16 = a2 + 1;
  *(_BYTE *)(*(_DWORD *)(a3 + 612) + 80) = 1;
  if ( v14 < 4 )
  {
    if ( _builtin_new(84) )
      v4 = sub_65B00(400, 66, 0);
    else
      v4 = 0;
    v5 = *(_DWORD *)(a3 + 4 * v16 + 728);
    if ( v4 != v5 )
    {
      if ( v5 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v5 + 8))(v5);
      *(_DWORD *)(a3 + 4 * v16 + 728) = v4;
      if ( v4 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v4 + 4))(v4);
    }
    sub_64600(sub_38CC0, a1);
    sub_65D00("CM_Speedometer_mph", "ui_icon_speedometer_m", 0, 0, -1, 1);
    sub_65D00("CM_Speedometer_kph", "ui_icon_speedometer_k", 1, 0, -1, 1);
    if ( _builtin_new(84) )
      v6 = sub_65B00(400, 65, 0);
    else
      v6 = 0;
    v7 = *(_DWORD *)(a3 + 4 * v16 + 712);
    if ( v6 != v7 )
    {
      if ( v7 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v7 + 8))(v7);
      *(_DWORD *)(a3 + 4 * v16 + 712) = v6;
      if ( v6 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v6 + 4))(v6);
    }
    return mcMenuGeneral__PopulateMenu_void(a1, v16, a3, a4);
  }
  else
  {
    sub_7A7D0(64, "ui_img_camera_pov", 0, 0);
    sub_7A7D0(64, "ui_img_camera_1", 0, 1);
    sub_7A7D0(64, "ui_img_camera_2", 0, 2);
    sub_7A7D0(64, "ui_img_camera_3", 0, 3);
    sub_7A7D0(64, "ui_img_camera_4", 0, 4);
    sub_7A7D0(62, "ui_img_rearview", 0, -1);
    sub_7A7D0(63, "ui_img_rotate_map", 0, -1);
    sub_7A7D0(65, "ui_img_icons_xray", 0, -1);
    sub_7A7D0(61, "ui_img_camera_cinematic", 0, -1);
    sub_7A7D0(66, "ui_img_speedometer", 0, -1);
    sub_7A7D0(59, "ui_controller_x", 1, -1);
    if ( _builtin_new(84) )
      v17 = sub_65B00(300, 53, 0);
    else
      v17 = 0;
    v18 = *(_DWORD *)(a3 + 744);
    if ( v17 != v18 )
    {
      if ( v18 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v18 + 8))(v18);
      *(_DWORD *)(a3 + 744) = v17;
      if ( v17 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v17 + 4))(v17);
    }
    v49 = *(_DWORD *)(a3 + 612);
    if ( v49 )
      (*(void (__thiscall **)(int, int))(*(_DWORD *)v49 + 4))(v49, v49);
    sub_64970(v49);
    sub_64600(sub_38CC0, a1);
    sub_65D00("CM_Movie_Subtitles_On", "ui_icon_on", 1, 0, -1, 1);
    sub_65D00("CM_Movie_Subtitles_Off", "ui_icon_off", 0, 0, -1, 1);
    sub_7A7D0(53, "ui_img_subtitles", 0, -1);
    if ( _builtin_new(84) )
      v19 = sub_65B00(200, 52, 0);
    else
      v19 = 0;
    v20 = *(_DWORD *)(a3 + 608);
    if ( v19 != v20 )
    {
      if ( v20 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v20 + 8))(v20);
      *(_DWORD *)(a3 + 608) = v19;
      if ( v19 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v19 + 4))(v19);
    }
    v50 = 1;
    v37 = 0;
    v27 = *(_DWORD *)(a3 + 612);
    if ( v27 )
      (*(void (__thiscall **)(int, int, _DWORD, int))(*(_DWORD *)v27 + 4))(v27, v27, 0, 1);
    sub_65D00("CM_Controller_Setup", "ui_icon_opt_controller_x", -1, v27, v37, v50);
    v51 = 1;
    v38 = 1;
    v28 = *(_DWORD *)(a3 + 744);
    if ( v28 )
      (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v28 + 4))(v28, v28, 1, 1);
    sub_65D00("CM_Game", "ui_icon_option_game", -1, v28, v38, v51);
    v52 = 1;
    v39 = 2;
    v29 = *(_DWORD *)(a3 + 760);
    if ( v29 )
      (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v29 + 4))(v29, v29, 2, 1);
    sub_65D00("CM_Audio", "ui_icon_opt_audio", -1, v29, v39, v52);
    sub_65D00("CM_Credits", "ui_icon_option_credits", -1, 0, 3, 1);
    if ( (unsigned __int8)sub_207FC0("languageselect") || dword_3AC6D8 || byte_541304 )
      sub_65D00("CM_Language_Select", "ui_icon_language_select", -1, 0, 5, 1);
    sub_65D00("CM_Cheat_Codes", "ui_icon_option_cheat", -1, 0, 4, 1);
    *(_BYTE *)(*(_DWORD *)(a3 + 608) + 80) = 1;
    sub_7A7D0(52, "ui_img_controllerlayout_x", 0, 0);
    sub_7A7D0(52, "ui_img_option_game", 0, 1);
    sub_7A7D0(52, "ui_img_audio", 0, 2);
    sub_7A7D0(52, "ui_img_option_credits", 0, 3);
    sub_7A7D0(52, "ui_img_language_select", 0, 5);
    sub_7A7D0(52, "ui_img_option_cheat", 0, 4);
    if ( _builtin_new(84) )
      v21 = sub_65B00(100, 0, 0);
    else
      v21 = 0;
    v22 = *(_DWORD *)(a3 + 52);
    if ( v21 != v22 )
    {
      if ( v22 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v22 + 8))(v22);
      *(_DWORD *)(a3 + 52) = v21;
      if ( v21 )
        (*(void (__thiscall **)(int))(*(_DWORD *)v21 + 4))(v21);
    }
    sub_64F60(off_34DEA4[0], 0);
    sub_645C0(sub_3D890, a1);
    sub_64600(sub_3DCB0, a1);
    sub_64640(sub_38C10, a1);
    v53 = 1;
    v40 = 1;
    v30 = *(_DWORD *)(a3 + 64);
    if ( v30 )
      (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v30 + 4))(v30, v30, 1, 1);
    sub_65D00("CM_Career", "ui_icon_career", 1, v30, v40, v53);
    v54 = 1;
    v41 = 0;
    v31 = *(_DWORD *)(a3 + 60);
    if ( v31 )
      (*(void (__thiscall **)(int, int, _DWORD, int))(*(_DWORD *)v31 + 4))(v31, v31, 0, 1);
    sub_65D00("CM_Arcade", "ui_icon_arcade", 0, v31, v41, v54);
    if ( !(unsigned __int8)sub_207FC0("nonet") )
    {
      v55 = 1;
      v42 = 2;
      v32 = *(_DWORD *)(a3 + 584);
      if ( v32 )
        (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v32 + 4))(v32, v32, 2, 1);
      sub_65D00("CM_Networking", "ui_icon_network", 2, v32, v42, v55);
    }
    sub_645A0(sub_38B10, a1);
    v56 = 1;
    v43 = 3;
    v33 = *(_DWORD *)(a3 + 60);
    if ( v33 )
      (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v33 + 4))(v33, v33, 3, 1);
    sub_65D00("CM_Race_Editor", "ui_icon_raceditor", 3, v33, v43, v56);
    v57 = 1;
    v44 = 4;
    v34 = *(_DWORD *)(a3 + 608);
    if ( v34 )
      (*(void (__thiscall **)(int, int, int, int))(*(_DWORD *)v34 + 4))(v34, v34, 4, 1);
    sub_65D00("CM_Options", "ui_icon_options", 4, v34, v44, v57);
    *(_BYTE *)(*(_DWORD *)(a3 + 52) + 80) = 1;
    sub_7A7D0(0, "ui_img_career", 0, 1);
    sub_7A7D0(0, "ui_img_arcade", 0, 0);
    sub_7A7D0(0, "ui_img_networking", 0, 2);
    sub_7A7D0(0, "ui_img_raceeditor", 0, 3);
    sub_7A7D0(0, "ui_img_options_x", 0, 4);
    sub_7A7D0(0, "ui_img_options_x", 0, 5);
    v58 = *(_DWORD *)(a3 + 52);
    if ( v58 )
      (*(void (__thiscall **)(int, int))(*(_DWORD *)v58 + 4))(v58, v58);
    sub_648C0(v58);
    (*(void (__thiscall **)(_DWORD))(**(_DWORD **)(a3 + 20) + 148))(*(_DWORD *)(a3 + 20));
    v23 = *(_DWORD *)(a3 + 24);
    if ( v23 )
      (*(void (__thiscall **)(int))(*(_DWORD *)v23 + 148))(v23);
    result = (*(int (**)(void))(*(_DWORD *)v60 + 8))();
    if ( v59 )
      return (*(int (**)(void))(*(_DWORD *)v59 + 8))();
  }
  return result;
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

### `hudMapLocal__Init_int_hudHud__ptr__hudHud__Anchors`
- **MC2 Xbox VA:** `0x0B4FA0..0xb5065` (208 B) | **MC3 Xbox VA:** `0x0B90F0` (197 B, delta: `-11 B`) | **MC3 PS2 VA:** `0x285F18`
- **Match Method:** `seed` | **REA Function Evidence ID:** `ev_5a637a395c4528bf70aa7dc7e62201a96d6b779b98eafac5c64e8df5915cf3e6`

```cpp
int __thiscall hudMapLocal__Init_int_hudHud__ptr__hudHud__Anchors(char *this, int a2, const char *a3)
{
  _BYTE v5[100]; // [esp+Ch] [ebp-64h] BYREF

  strlen(v5, 100, "%s.Left", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(3, v5, this, 1, 0);
  strlen(v5, 100, "%s.Bottom", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(3, v5, this + 1, 1, 0);
  strlen(v5, 100, "%s.Width", a3);
  datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(3, v5, this + 2, 1, 0);
  strlen(v5, 100, "%s.Height", a3);
  return datParser__AddRecord_int_char_const__ptr__void__ptr__unsigned_short_datCallback__ptr(3, v5, this + 3, 1, 0);
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

## 2. Full Symbol Equivalence Table (244 functions)

| MC2 Xbox VA | MC3 Xbox VA | MC3 PS2 VA | Symbol | MC2 Size | MC3 Size | Delta | Method |
|---|---|---|---|---:|---:|---:|---|
| `0x019F43` | `0x029010` | `0x1A9A10` | `mcLayerMovie__Load_void` | 297 | 11 | -286 | `seed` |
| `0x01C620` | `0x026310` | `0x1B2788` | `mcNetManagerDerived__PostQuit_int_unsigned_wchar_t_const__ptr__net__eQuitReason_int_int` | 176 | 91 | -85 | `seed` |
| `0x01C7C0` | `0x026FD0` | `0x1B2D40` | `mcNetManagerDerived__PostQuit_int_unsigned_wchar_t_const__ptr__net__eQuitReason_int_int` | 898 | 855 | -43 | `seed` |
| `0x022290` | `0x0BDA40` | `0x27D150` | `hudMap__Init_int_hudHud__ptr__hudHud__Anchors` | 68 | 287 | +219 | `seed` |
| `0x022DF9` | `0x1881A0` | `0x35A190` | `mcMenuRaceEditor__PopulateMenu_void` | 28 | 1131 | +1103 | `seed` |
| `0x02DAC0` | `0x0477C0` | `-` | `mcFeInternet__FriendsGetName_int` | 16 | 13 | -3 | `insn_signature` |
| `0x037EC0` | `0x15AA30` | `0x3647A8` | `mcMoviePlayer__Play_char_const__ptr` | 431 | 594 | +163 | `seed` |
| `0x038FF0` | `0x162590` | `-` | `mcMenuShell__ChangeState_MenuStates` | 48 | 45 | -3 | `insn_signature` |
| `0x03EB9E` | `0x18F160` | `0x3843E0` | `mcMenuAudio__PopulateMenu_void` | 1122 | 890 | -232 | `seed` |
| `0x03F000` | `0x18E2C0` | `0x3488E0` | `mcMenuGeneral__PopulateMenu_void` | 851 | 872 | +21 | `seed` |
| `0x03F358` | `0x18E940` | `0x352528` | `mcMenuHud__PopulateMenu_void` | 1099 | 993 | -106 | `seed` |
| `0x040AC4` | `0x15B640` | `0x37C090` | `mcChatListMenu__FileIO_datParser__ref` | 124 | 177 | +53 | `seed` |
| `0x040B40` | `0x18C010` | `-` | `mcMenuNet__mcMenuNet_char_const__ptr__int` | 448 | 125 | -323 | `seed` |
| `0x0415D0` | `0x15E720` | `0x379990` | `mcNetworkWaiting__DisplayHostLostMessage_net__eQuitReason` | 480 | 197 | -283 | `seed` |
| `0x041E78` | `0x15BE30` | `0x379F98` | `mcNetworkWaiting__FileIO_datParser__ref` | 1032 | 3158 | +2126 | `seed` |
| `0x043B5F` | `0x15EA90` | `0x378588` | `mcNetworkWaitingCountdown__mcNetworkWaitingCountdown_void` | 2385 | 1057 | -1328 | `seed` |
| `0x047B2D` | `0x165E50` | `0x34B9D0` | `mcMenuCustom__GetTODString_int` | 298 | 42 | -256 | `seed` |
| `0x047C57` | `0x1851F0` | `0x34D408` | `mcMenuCustomRaceType__GetTeamModeString_int` | 2607 | 69 | -2538 | `seed` |
| `0x04AA44` | `-` | `0x36D250` | `mcNetworkHostSelect__JoinFailed_net__eQuitReason` | 192 | 0 | +0 | `ps2_callgraph` |
| `0x04D9B0` | `0x33D600` | `0x578538` | `mcFeMemCard__FileIO_datParser__ref` | 144 | 106 | -38 | `seed` |
| `0x04DA70` | `0x33D790` | `0x575860` | `mcFeMemCard__ShowAccessWarning_mcFeMemCard__AccessType` | 176 | 200 | +24 | `seed` |
| `0x04E040` | `0x33EC10` | `0x574828` | `mcFeMemCard__CreateWidgets_void` | 448 | 571 | +123 | `seed` |
| `0x04E322` | `0x33E1C0` | `0x575F88` | `mcFeMemCard__UpdateSavegameSelectList_void` | 158 | 2367 | +2209 | `seed` |
| `0x04F647` | `0x33F3F0` | `0x577D20` | `mcFeMemCard__HandleMemcardError_mcFeMemCard__Operation_int` | 537 | 564 | +27 | `seed` |
| `0x052876` | `0x176A50` | `0x370E10` | `mcNetworkRecentPlayers__PopulateEditPlayer_unsigned_wchar_t_const__ptr__netGUID_int` | 1674 | 1906 | +232 | `seed` |
| `0x054780` | `0x16EDD0` | `0x36B9E0` | `mcNetworkFriendsList__PopulateFriendPopup_void` | 960 | 908 | -52 | `seed` |
| `0x0550F0` | `0x16DCF0` | `0x36BFE8` | `mcNetworkFriendsList__PopulateMenu_void` | 832 | 1496 | +664 | `seed` |
| `0x055F60` | `0x15E320` | `-` | `mcNetworkWaiting__Show_bool` | 96 | 83 | -13 | `insn_signature` |
| `0x0584E0` | `0x17D830` | `0x36A7D0` | `mcNetworkFilter__Update_void` | 384 | 186 | -198 | `seed` |
| `0x058F30` | `0x180350` | `0x372530` | `mcNetworkSelect__Update_void` | 96 | 306 | +210 | `seed` |
| `0x0620F0` | `0x169060` | `0x366300` | `mcMenuMsgBox__FileIO_datParser__ref` | 80 | 38 | -42 | `seed` |
| `0x062140` | `0x169220` | `0x366368` | `mcMenuMsgBoxListMenu__mcMenuMsgBoxListMenu_char_const__ptr__int` | 96 | 82 | -14 | `seed` |
| `0x062B00` | `0x16A0A0` | `0x3650C0` | `mcMenuMsgBox__CreateWidgets_void` | 480 | 521 | +41 | `seed` |
| `0x0634B0` | `0x192D30` | `0x381568` | `TextAnimConfig__FileIO_datParser__ref__char_const__ptr` | 112 | 111 | -1 | `seed` |
| `0x063560` | `0x164320` | `0x33B500` | `mcMenuShell__ShowConfirmationSimple_char_const__ptr__unsigned_int_mcMenuMsgBox__MsgItem` | 32 | 64 | +32 | `seed` |
| `0x063850` | `0x15DDB0` | `0x3772C0` | `mcNetworkWaiting__mcNetworkWaiting_char_const__ptr__int` | 266 | 1008 | +742 | `seed` |
| `0x064330` | `0x1698B0` | `-` | `mcMenuMsgBox__mcMenuMsgBox_char_const__ptr__int` | 48 | 123 | +75 | `prop_round_1` |
| `0x066D1D` | `0x34CEF0` | `0x585290` | `mcUiKeyboard__DoRendering_void` | 1122 | 356 | -766 | `seed` |
| `0x0673B0` | `0x34D890` | `-` | `mcUiKeyboard__StripLeadingAndTrailingSpaces_char__ptr__int_char_const__ptr` | 112 | 104 | -8 | `insn_signature` |
| `0x067420` | `0x34D920` | `0x5861F8` | `mcUiKeyboard__SetMaxAllowedMessageLength_int` | 624 | 627 | +3 | `seed` |
| `0x067690` | `0x34FDE0` | `0x582468` | `mcUiKeyboard__mcUiKeyboard_char_const__ptr__int` | 464 | 597 | +133 | `seed` |
| `0x067920` | `0x34DC70` | `0x5829C0` | `mcUiKeyboard__InitializeKeyboard_int_int_int_char_const__ptr__int` | 1920 | 6196 | +4276 | `seed` |
| `0x068970` | `0x044650` | `-` | `hudDropCounter__SetCursor_void` | 96 | 88 | -8 | `prop_round_1` |
| `0x0689D0` | `0x350970` | `-` | `mcUiHeading__FileIO_datParser__ref` | 48 | 48 | +0 | `prop_round_2` |
| `0x069000` | `0x350A70` | `0x582030` | `mcUiHeading__FileIO_datParser__ref` | 379 | 858 | +479 | `seed` |
| `0x07A120` | `0x348520` | `0x580EF0` | `mcUiGroup__CreateWidgets_void` | 352 | 344 | -8 | `seed` |
| `0x07A370` | `0x348680` | `-` | `mcUiGroup__DestroyWidgets_void` | 32 | 24 | -8 | `prop_round_1` |
| `0x07B880` | `0x348780` | `0x587048` | `mcUiListMenu__PrepareForUsage_void` | 128 | 123 | -5 | `seed` |
| `0x07BA40` | `0x3488F0` | `0x587DF8` | `mcUiListMenu__DefineTextColumn_int_int_bool` | 32 | 55 | +23 | `seed` |
| `0x07C0D0` | `0x349370` | `0x58ADA0` | `mcUiListMenu__columnData__FileIO_char_const__ptr__datParser__ref` | 848 | 1026 | +178 | `seed` |
| `0x07C420` | `0x349780` | `0x58B268` | `mcUiListMenu__columnData__FileIO_char_const__ptr__datParser__ref` | 160 | 200 | +40 | `seed` |
| `0x07DB50` | `0x34ADB0` | `0x587D58` | `mcUiListMenu__SetInput_atDerivedPtr_uiInput_atPtr_uiWidget_const__ref` | 17 | 51 | +34 | `seed` |
| `0x07DDC0` | `0x2BDAD0` | `-` | `mcMenuControllerConfig__ResetPrevAxisValues_void` | 64 | 52 | -12 | `insn_signature` |
| `0x07FC40` | `0x2C9960` | `0x5E8110` | `mcFeMemCard__AllWidgets__AllWidgets_void` | 16 | 6 | -10 | `seed` |
| `0x096DA8` | `0x16ADD0` | `0x358C40` | `mcMenuPause__DoMoveToNextRace_void` | 2109 | 1870 | -239 | `seed` |
| `0x098186` | `0x16BFA0` | `0x35AA10` | `mcMenuRaceOver__PopulateMenu_int` | 550 | 2721 | +2171 | `seed` |
| `0x0983AC` | `0x16B51E` | `0x34FFD0` | `mcMenuRaceOver__HandleCareerAndCruiseSelection_int` | 2071 | 802 | -1269 | `career_semantic_seed` |
| `0x0997C0` | `0x161CE0` | `0x33B5D0` | `mcMenuShell__ActivateConfirmation_void` | 574 | 1282 | +708 | `seed` |
| `0x099AA0` | `-` | `0x33BD80` | `mcMenuShell__PopulateHostQuitMenu_net__eQuitReason` | 752 | 0 | +0 | `ps2_callgraph` |
| `0x09AB90` | `-` | `-` | `mcHud__ShowFindHookmanPrompt_void` | 608 | null | +null | `career_semantic_seed` |
| `0x0A3370` | `0x13A690` | `0x33EC20` | `mcMenuArcade__GetRaceTypeName_int_int` | 187 | 214 | +27 | `seed` |
| `0x0B1580` | `0x0D3040` | `-` | `hudZoneMeter__GetTypeName_void` | 64 | 186 | +122 | `prop_round_3` |
| `0x0B15C0` | `0x0B7DC0` | `0x5BBE08` | `hudChat__GetTypeName_void` | 16 | 37 | +21 | `seed` |
| `0x0B18A0` | `0x156C90` | `0x341DF8` | `mcMenuBrain__CreateWidgets_bool_bool` | 304 | 6714 | +6410 | `seed` |
| `0x0B19D0` | `0x0B7D00` | `0x5BBDF8` | `hudChat__SharedData__GetTypeName_void` | 16 | 13 | -3 | `seed` |
| `0x0B4F90` | `0x0B8890` | `0x5BC280` | `hudMap__SharedDataAllTypes__GetTypeName_void` | 16 | 2121 | +2105 | `seed` |
| `0x0B4FA0` | `0x0B90F0` | `0x285F18` | `hudMapLocal__Init_int_hudHud__ptr__hudHud__Anchors` | 208 | 197 | -11 | `seed` |
| `0x0B5820` | `0x0BA0D0` | `0x287DB0` | `hudMapLocal__SharedDataLocalMap__TextureData__FileIO_datParser__ref__char_const__ptr` | 320 | 310 | -10 | `seed` |
| `0x0B5C70` | `0x0BA260` | `0x5BC3B0` | `hudMapGlobal__SharedDataGlobalMap__GetTypeName_void` | 16 | 120 | +104 | `seed` |
| `0x0B5C80` | `0x0BA2F0` | `0x288BD8` | `hudMapGlobal__SharedDataGlobalMap__FileIO_datParser__ref` | 160 | 151 | -9 | `seed` |
| `0x0B5D90` | `0x0BAB00` | `0x5BC298` | `hudMap__GetTypeName_void` | 16 | 246 | +230 | `seed` |
| `0x0B617F` | `0x0BC800` | `0x2855E0` | `hudMap__SharedDataAllTypes__FileIO_datParser__ref` | 261 | 143 | -118 | `seed` |
| `0x0B6360` | `0x0BEAC0` | `0x5BC338` | `hudMapLocal__GetTypeName_void` | 16 | 137 | +121 | `seed` |
| `0x0B64C0` | `0x0BCFA0` | `0x5BC310` | `hudMapLocal__SharedDataLocalMap__GetTypeName_void` | 16 | 408 | +392 | `seed` |
| `0x0B64D0` | `0x0BD150` | `0x287AA0` | `hudMapLocal__SharedDataLocalMap__FileIO_datParser__ref` | 512 | 507 | -5 | `seed` |
| `0x0B6750` | `0x0BECE0` | `0x5BC3C8` | `hudMapGlobal__GetTypeName_void` | 16 | 130 | +114 | `seed` |
| `0x0B8590` | `0x0B4640` | `0x5BCDA8` | `hudSpeedometer__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0B87D0` | `0x0B3390` | `0x5BCDD8` | `hudSplashImage__GetTypeName_void` | 16 | 247 | +231 | `seed` |
| `0x0B89A0` | `0x0B3590` | `0x297170` | `hudSplashBase__FileIO_datParser__ref` | 48 | 33 | -15 | `prop_round_2` |
| `0x0B8A30` | `0x0B35C0` | `0x5BCE08` | `hudSplashImage__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0B8B80` | `0x0B35D0` | `0x5BCE40` | `hudSplashText__GetTypeName_void` | 16 | 90 | +74 | `seed` |
| `0x0B8C00` | `0x0B3750` | `0x297658` | `hudSplashText__FileIO_datParser__ref` | 48 | 126 | +78 | `seed` |
| `0x0B8E10` | `0x0B3A60` | `0x297B78` | `hudSplashToTimerAnim__FileIO_datParser__ref__char_const__ptr` | 176 | 172 | -4 | `seed` |
| `0x0B90D0` | `0x0B3D60` | `0x297FE8` | `hudSplashSimpleZoomInAnim__FileIO_datParser__ref__char_const__ptr` | 336 | 327 | -9 | `seed` |
| `0x0B9490` | `0x0B4289` | `0x2986A8` | `hudSplashToTimerAnim__FileIO_datParser__ref__char_const__ptr` | 384 | 500 | +116 | `seed` |
| `0x0B9740` | `0x0B4B50` | `0x5BCE50` | `hudSplashTranslatedText__GetTypeName_void` | 16 | 110 | +94 | `seed` |
| `0x0B97F0` | `0x0B4BD0` | `0x5BCE60` | `hudSplashDynamicText__GetTypeName_void` | 16 | 156 | +140 | `seed` |
| `0x0B98E0` | `0x0B4DF0` | `0x295880` | `hudSplashMgr__Init_int` | 2096 | 5437 | +3341 | `seed` |
| `0x0BA1B0` | `0x0DBF70` | `0x279038` | `hudElement__Init_int_hudHud__ptr__hudHud__Anchors_char_const__ptr` | 176 | 141 | -35 | `seed` |
| `0x0BA260` | `0x0DC030` | `-` | `hudElement__SetInitialized_bool` | 16 | 10 | -6 | `prop_round_1` |
| `0x0BA290` | `0x0DC1F0` | `0x279460` | `hudElement__FileIO_datParser__ref` | 64 | 63 | -1 | `seed` |
| `0x0BA820` | `0x0DC7F0` | `0x2740C8` | `hudChatBox__SharedData__GetTypeName_void` | 128 | 166 | +38 | `seed` |
| `0x0BA8A0` | `0x0DC8A0` | `0x5BBE18` | `hudChatBox__SharedData__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BA8D0` | `0x0DC8B0` | `0x274218` | `hudChatBox__SharedData__FileIO_datParser__ref` | 208 | 195 | -13 | `seed` |
| `0x0BAB10` | `-` | `0x294248` | `hudSharedData__hudSharedData_void` | 128 | 0 | +0 | `ps2_callgraph` |
| `0x0BABD0` | `0x0D1C20` | `0x5BCB20` | `hudNitro__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BB0B0` | `0x0D1F20` | `0x279A68` | `hudFlag__GetTypeName_void` | 48 | 120 | +72 | `seed` |
| `0x0BB230` | `0x0D2180` | `0x5BC130` | `hudFlag__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BB2C0` | `0x0D2190` | `0x5BC120` | `hudFlag__SharedData__GetTypeName_void` | 16 | 141 | +125 | `seed` |
| `0x0BB2D0` | `0x0D2230` | `0x279B78` | `hudFlag__SharedData__FileIO_datParser__ref` | 128 | 91 | -37 | `seed` |
| `0x0BB5F0` | `0x0D25D0` | `0x28C038` | `hudPowerup__FileIO_datParser__ref` | 96 | 85 | -11 | `seed` |
| `0x0BB6A0` | `0x0D2680` | `0x5BCB60` | `hudPowerup__SharedData__GetTypeName_void` | 16 | 96 | +80 | `seed` |
| `0x0BB760` | `0x0D2730` | `0x5BCB70` | `hudPowerup__GetTypeName_void` | 16 | 117 | +101 | `seed` |
| `0x0BB7D0` | `0x0D6890` | `0x2782A8` | `hudDropCounter__Init_int_hudHud__ptr__hudHud__Anchors` | 160 | 319 | +159 | `seed` |
| `0x0BB8C0` | `0x0D69F0` | `0x278E50` | `hudDropCounter__SharedData__SharedData_void` | 80 | 115 | +35 | `seed` |
| `0x0BB910` | `0x0D6850` | `0x5BC0B8` | `hudDropCounter__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 64 | +48 | `seed` |
| `0x0BB940` | `0x0D69E0` | `0x5BC0C8` | `hudDropCounter__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BBA30` | `0x0D6AE0` | `0x5BC0D8` | `hudDropCounter__GetTypeName_void` | 16 | 97 | +81 | `seed` |
| `0x0BBD40` | `0x0D7230` | `0x27B5F8` | `hudLapCounter__Init_int_hudHud__ptr__hudHud__Anchors` | 224 | 458 | +234 | `seed` |
| `0x0BBF40` | `0x0D7970` | `-` | `hudLapCounter__FileIO_datParser__ref` | 64 | 50 | -14 | `prop_round_1` |
| `0x0BBFD0` | `0x0D7A10` | `0x27CB40` | `hudLapCounter__FileIO_datParser__ref` | 64 | 69 | +5 | `seed` |
| `0x0BC010` | `0x0D7A70` | `0x27CBE0` | `hudLapCounter__SharedDataNumberOfViewports__GetTypeName_void` | 80 | 97 | +17 | `seed` |
| `0x0BC060` | `0x0D7AE0` | `0x5BC230` | `hudLapCounter__SharedData__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BC090` | `0x0D7AF0` | `0x5BC240` | `hudLapCounter__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BC160` | `0x0D7BB0` | `0x5BC250` | `hudLapCounter__GetTypeName_void` | 16 | 237 | +221 | `seed` |
| `0x0BC1E0` | `0x0D7D30` | `0x27B8B0` | `hudLapCounter__Display_void` | 1104 | 1921 | +817 | `seed` |
| `0x0BC650` | `0x0D84F0` | `0x291BC8` | `hudRankDisplay__Init_int_hudHud__ptr__hudHud__Anchors` | 176 | 215 | +39 | `seed` |
| `0x0BC798` | `0x0D8630` | `0x2928A8` | `hudRankDisplay__SharedDataNumberOfViewports__GetTypeName_void` | 40 | 97 | +57 | `seed` |
| `0x0BC7C0` | `0x0D86A0` | `0x5BCCA0` | `hudRankDisplay__SharedData__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BC830` | `0x0D8720` | `0x5BCCB0` | `hudRankDisplay__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BC8E0` | `0x0D87A0` | `0x5BCCC0` | `hudRankDisplay__GetTypeName_void` | 16 | 153 | +137 | `seed` |
| `0x0BCD90` | `0x0D9050` | `0x274F08` | `mcHudClock__SharedDataNumberOfViewports__GetTypeName_void` | 80 | 116 | +36 | `seed` |
| `0x0BCDE0` | `0x0D90D0` | `0x5BBE70` | `mcHudClock__SharedData__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BCE40` | `0x0D9110` | `0x5BBE80` | `mcHudClock__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BCEF0` | `0x0D9190` | `0x5BBE90` | `mcHudClock__GetTypeName_void` | 16 | 153 | +137 | `seed` |
| `0x0BD320` | `0x0D98F0` | `0x5BCC30` | `mcHudTimer__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 143 | +127 | `seed` |
| `0x0BD330` | `0x0D9990` | `0x28E9D8` | `mcHudTimer__SharedData__FileIO_datParser__ref` | 176 | 151 | -25 | `seed` |
| `0x0BD400` | `0x0D9A30` | `0x5BCC40` | `mcHudTimer__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BD500` | `0x0D9AE0` | `0x5BCC50` | `mcHudTimer__GetTypeName_void` | 16 | 184 | +168 | `seed` |
| `0x0BD860` | `0x0D43A0` | `0x28AED8` | `hudNitro__Init_int_hudHud__ptr__hudHud__Anchors` | 144 | 149 | +5 | `seed` |
| `0x0BDC40` | `0x0D4610` | `0x28B4C8` | `hudNitro__SharedDataNumberOfViewports__GetTypeName_void` | 416 | 310 | -106 | `seed` |
| `0x0BDE00` | `0x0D4750` | `0x5BCB10` | `hudNitro__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0BDF10` | `0x0D4860` | `0x5BCB00` | `hudNitro__SharedData__GetTypeName_void` | 16 | 147 | +131 | `seed` |
| `0x0BE030` | `0x0D4F70` | `0x28C400` | `hudSSTurbo__Init_int_hudHud__ptr__hudHud__Anchors` | 256 | 304 | +48 | `seed` |
| `0x0BE5B0` | `0x0D2DD0` | `0x28D058` | `hudZoneMeter__SharedDataNumberOfViewports__GetTypeName_void` | 416 | 494 | +78 | `seed` |
| `0x0BE770` | `0x0D4CC0` | `0x5BCBD0` | `hudSSTurbo__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 402 | +386 | `seed` |
| `0x0BE830` | `0x0D4EE0` | `0x5BCBE0` | `hudSSTurbo__GetTypeName_void` | 16 | 127 | +111 | `seed` |
| `0x0BE8D0` | `0x0D5340` | `0x5BCBC0` | `hudSSTurbo__SharedData__GetTypeName_void` | 16 | 162 | +146 | `seed` |
| `0x0BE8E0` | `0x0D5400` | `0x28CF50` | `hudSSTurbo__SharedData__FileIO_datParser__ref` | 192 | 135 | -57 | `seed` |
| `0x0BEB00` | `0x0D5550` | `0x275260` | `hudDamage__Init_int_hudHud__ptr__hudHud__Anchors` | 160 | 181 | +21 | `seed` |
| `0x0BEF40` | `0x0D59B0` | `0x275EF0` | `hudDamage__SharedData__TextureData__FileIO_datParser__ref__char_const__ptr` | 320 | 310 | -10 | `seed` |
| `0x0BF410` | `0x0D5EB0` | `-` | `hudDamage__SharedData__FileIO_datParser__ref` | 160 | 199 | +39 | `seed` |
| `0x0BF4C0` | `0x0D5F80` | `0x275DE0` | `hudDamage__SharedData__FileIO_datParser__ref` | 224 | 143 | -81 | `seed` |
| `0x0BF650` | `0x0D60A0` | `0x279EC8` | `hudGear__SetHudColor_mcPackedColor4_const__ref` | 192 | 295 | +103 | `seed` |
| `0x0BFA10` | `0x0D64D0` | `0x5BC190` | `hudGear__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 218 | +202 | `seed` |
| `0x0BFAA0` | `0x0D6670` | `0x5BC1A0` | `hudGear__GetTypeName_void` | 16 | 101 | +85 | `seed` |
| `0x0BFB20` | `0x0D66F0` | `0x5BC180` | `hudGear__SharedData__GetTypeName_void` | 16 | 105 | +89 | `seed` |
| `0x0BFC60` | `0x0D3A50` | `-` | `hudTachometer__Init_int_hudHud__ptr__hudHud__Anchors` | 121 | 76 | -45 | `seed` |
| `0x0BFCD9` | `0x0D3A9C` | `0x298AC8` | `hudTachometer__Init_int_hudHud__ptr__hudHud__Anchors` | 167 | 382 | +215 | `seed` |
| `0x0BFDA0` | `0x0D9FF0` | `0x295350` | `hudSpeedometer__SharedDataNumberOfViewports__GetTypeName_void` | 320 | 494 | +174 | `seed` |
| `0x0C04C0` | `0x0D41B0` | `-` | `hudTachometer__SharedData__FileIO_datParser__ref` | 128 | 196 | +68 | `seed` |
| `0x0C0540` | `0x0D4280` | `0x2997E0` | `hudTachometer__SharedData__FileIO_datParser__ref` | 128 | 143 | +15 | `seed` |
| `0x0C0990` | `0x0DA1E0` | `0x5BCD98` | `hudSpeedometer__SharedDataNumberOfViewports__GetTypeName_void` | 16 | 6 | -10 | `seed` |
| `0x0C0AC0` | `0x0DA260` | `0x294498` | `hudSpeedometer__Init_int_hudHud__ptr__hudHud__Anchors` | 192 | 135 | -57 | `seed` |
| `0x0C0E70` | `0x0DAFF0` | `0x294000` | `hudRearViewMirror__SharedDataNumberOfViewports__GetTypeName_void` | 320 | 310 | -10 | `seed` |
| `0x0C1040` | `0x0DB1C0` | `0x5BCD30` | `hudRearViewMirror__GetTypeName_void` | 16 | 178 | +162 | `seed` |
| `0x0C1050` | `0x0DB290` | `0x292CF0` | `hudRearViewMirror__Init_int_hudHud__ptr__hudHud__Anchors` | 144 | 308 | +164 | `seed` |
| `0x0C13E0` | `0x0DB940` | `0x5BCD10` | `hudRearViewMirror__SharedData__GetTypeName_void` | 16 | 215 | +199 | `seed` |
| `0x0C13F0` | `0x0DBA30` | `0x293E40` | `hudRearViewMirror__SharedData__FileIO_datParser__ref` | 224 | 223 | -1 | `seed` |
| `0x0C18A0` | `0x0D10E0` | `0x5BCFD8` | `hudArrow__GetTypeName_void` | 16 | 176 | +160 | `seed` |
| `0x0C18B0` | `0x0D11A0` | `0x29C090` | `hudArrow__Init_int` | 240 | 408 | +168 | `seed` |
| `0x0C19A0` | `0x0D1370` | `0x29CB60` | `hudArrow__FileIO_datParser__ref` | 224 | 210 | -14 | `seed` |
| `0x0C77A0` | `0x1EC140` | `0x3FE580` | `aiBrainHookman__RestartCruise_void` | 304 | 272 | -32 | `career_semantic_seed` |
| `0x0FC610` | `0x12EBE0` | `0x30C8E8` | `mcCarFluidTune__FileIO_datParser__ref` | 144 | 123 | -21 | `seed` |
| `0x10EC80` | `0x082520` | `0x232BA8` | `mcTrainBuilder__FindTrainType_char_const__ptr` | 128 | 126 | -2 | `seed` |
| `0x10ED00` | `-` | `0x233148` | `mcTrainBuilder__GetTrainTrack_int_const` | 16 | 0 | +0 | `ps2_callgraph` |
| `0x10EDF0` | `0x0827B8` | `0x2328C8` | `mcTrainBuilder__LoadTrainSegments_mcTrain__ref__datBaseTokenizer__ref` | 304 | 424 | +120 | `seed` |
| `0x10F120` | `0x082C80` | `0x232430` | `mcTrainBuilder__LoadTrainTypes_char_const__ptr` | 352 | 352 | +0 | `seed` |
| `0x110C80` | `0x2B7C60` | `0x5017F0` | `aiRailNetwork__GetRoad_int_const` | 16 | 15 | -1 | `seed` |
| `0x110CA0` | `0x2B7C80` | `0x501820` | `aiRailNetwork__GetTrafficControl_int_const` | 16 | 15 | -1 | `seed` |
| `0x112880` | `0x2B97F0` | `0x5035A0` | `aiRailNetwork__FindVerifiedRoadId_Vector3_const__ref__const` | 144 | 160 | +16 | `seed` |
| `0x112CD0` | `0x2B99A0` | `0x503448` | `aiRailNetwork__LoadOverridenRoad_datAsciiTokenizer__ref` | 217 | 213 | -4 | `seed` |
| `0x112FD0` | `0x2B9A80` | `0x5032F8` | `aiRailNetwork__LoadRailNetworkOverrides_char_const__ptr` | 256 | 242 | -14 | `seed` |
| `0x113150` | `0x2B9C00` | `0x503798` | `aiRailNetwork__LoadRailNetwork_char_const__ptr` | 1536 | 1452 | -84 | `seed` |
| `0x123240` | `0x3342D0` | `0x564790` | `mcPlaneSplash__FileIO_datParser__ref` | 288 | 283 | -5 | `seed` |
| `0x14F300` | `0x277530` | `0x4C0880` | `mcProgressManager__SetupCareerCruise_int` | 528 | 240 | -288 | `career_semantic_seed` |
| `0x14F670` | `-` | `-` | `mcProgressManager__AreMoviesDisabled_void` | 32 | null | +null | `career_callgraph` |
| `0x14F830` | `0x277620` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreCityMovie_int` | 144 | 320 | +176 | `career_callgraph` |
| `0x14F8C0` | `0x277760` | `0x4C00C8` | `mcProgressManager__CheckAndRequestPostRaceMovie_int_int` | 304 | 464 | +160 | `career_callgraph` |
| `0x14F9F0` | `0x2774B0` | `0x4C0C78` | `mcProgressManager__CheckAndRequestPreRaceMovie_int_int` | 144 | 128 | -16 | `career_callgraph` |
| `0x1500D0` | `0x26F620` | `0x4B8DB0` | `mc__mcCityData__LoadMovieData_datAsciiTokenizer__ref` | 656 | 219 | -437 | `seed` |
| `0x1520A0` | `0x28B850` | `-` | `mcUnlocking__BuildCondition_char_const__ptr__char_const__ptr__uint__ref` | 368 | 1072 | +704 | `career_semantic_seed` |
| `0x152320` | `0x28AE00` | `0x4D50B0` | `mcUnlocking__CheckRule_uint_const` | 336 | 416 | +80 | `career_semantic_seed` |
| `0x15D960` | `0x202ED0` | `0x41E6C0` | `uiBase__GetTextOptions_txtLanguage__eLanguage__ref__unsigned_int__ref` | 48 | 33 | -15 | `seed` |
| `0x15E660` | `0x203BF0` | `0x5CA3A0` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___find_uiStaticString_const__ref` | 128 | 126 | -2 | `prop_round_2` |
| `0x15FA30` | `0x205350` | `0x5C8B40` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_atPtr_uiWidget__Select1st_pair_uiStaticString_const_atPtr_uiWidget_less_uiStaticString_allocator_atPtr_uiWidget___insert_unique_pair_uiStaticString_const_atPtr_uiWidget_const__ref` | 272 | 285 | +13 | `prop_round_4` |
| `0x15FB40` | `0x205470` | `0x5C9090` | `_Rb_tree_unsigned_int_pair_unsigned_int_const_atPtr_uiWidget__Select1st_pair_unsigned_int_const_atPtr_uiWidget_less_unsigned_int_allocator_atPtr_uiWidget___insert_unique_pair_unsigned_int_const_atPtr_uiWidget_const__ref` | 192 | 185 | -7 | `prop_round_4` |
| `0x15FC00` | `0x205590` | `0x5CA818` | `_Rb_tree_uiStaticString_pair_uiStaticString_const_unsigned_int__Select1st_pair_uiStaticString_const_unsigned_int_less_uiStaticString_allocator_unsigned_int___insert_unique_pair_uiStaticString_const_unsigned_int_const__ref` | 272 | 285 | +13 | `prop_round_2` |
| `0x1602B0` | `0x205730` | `0x41E7B0` | `uiBase__AddWidget_atPtr_uiWidget_const__ref` | 176 | 169 | -7 | `prop_round_3` |
| `0x160360` | `0x205880` | `0x41EAA8` | `uiBase__GetIDByName_char_const__ptr__bool__ptr` | 192 | 182 | -10 | `prop_round_1` |
| `0x160700` | `0x205B20` | `0x41D9A0` | `uiBase__uiBase_char_const__ptr` | 720 | 781 | +61 | `seed` |
| `0x161290` | `0x200FC0` | `0x428830` | `uiWidget__SetHasItsOwnTuningFile_bool` | 48 | 48 | +0 | `seed` |
| `0x161300` | `0x201030` | `0x428A88` | `uiWidget__SetShowInBank_bool` | 48 | 33 | -15 | `seed` |
| `0x161550` | `0x2011E0` | `0x4289A8` | `uiWidget__GetUniqueName_void_const` | 176 | 161 | -15 | `seed` |
| `0x161710` | `0x201370` | `0x427D28` | `uiWidget__GetMasterWidget_void` | 96 | 83 | -13 | `seed` |
| `0x161770` | `0x2013D0` | `0x428560` | `uiWidget__RegisterForFlatUpdate_int` | 96 | 87 | -9 | `seed` |
| `0x161820` | `0x2014D0` | `0x4286C0` | `uiWidget__RegisterByMaster_void` | 80 | 77 | -3 | `prop_round_1` |
| `0x162D60` | `0x202C30` | `0x425DB0` | `uiWidget__uiWidget_char_const__ptr__atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref__bool_bool` | 352 | 342 | -10 | `seed` |
| `0x163020` | `0x205E60` | `0x420918` | `uiInput__uiInput_char_const__ptr__atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 208 | 207 | -1 | `seed` |
| `0x164A80` | `0x20A1C0` | `0x422A00` | `uiMaster__RemoveFlatUpdateCallback_atPtr_uiWidget_const__ref` | 112 | 87 | -25 | `seed` |
| `0x164C80` | `0x20A270` | `0x4222B8` | `uiMaster__uiMaster_char_const__ptr__atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref__bool` | 112 | 126 | +14 | `seed` |
| `0x164E20` | `0x20A510` | `0x422898` | `uiMaster__AddFlatUpdateCallback_atPtr_uiWidget_const__ref__int` | 160 | 142 | -18 | `seed` |
| `0x164EC0` | `0x20A5A0` | `0x422AE0` | `uiMaster__AddWidget_atPtr_uiWidget_const__ref` | 96 | 94 | -2 | `prop_round_2` |
| `0x164F20` | `0x200A20` | `-` | `uiGroup__SetActiveState_bool` | 64 | 57 | -7 | `prop_round_1` |
| `0x1650B0` | `0x200C20` | `0x41FBA8` | `uiGroupBase__FileIO_datParser__ref` | 16 | 11 | -5 | `seed` |
| `0x165160` | `0x200D10` | `0x41F5D0` | `uiGroupBase__uiGroupBase_char_const__ptr__int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 240 | 251 | +11 | `seed` |
| `0x165270` | `0x200E30` | `-` | `uiGroup__uiGroup_char_const__ptr__int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 48 | 37 | -11 | `insn_signature` |
| `0x165310` | `0x207910` | `0x4257B8` | `uiVisual__FileIO_datParser__ref` | 144 | 132 | -12 | `seed` |
| `0x1654A0` | `0x207A90` | `0x425D48` | `uiVisualWithBlendColor__FileIO_datParser__ref` | 96 | 86 | -10 | `seed` |
| `0x165680` | `0x207D00` | `-` | `uiVisual__SetVisibleState_bool` | 96 | 95 | -1 | `prop_round_1` |
| `0x165860` | `0x207EF0` | `0x4253E8` | `uiVisual__InternalInit_void` | 96 | 93 | -3 | `seed` |
| `0x165A00` | `0x2080C0` | `0x425310` | `uiVisual__uiVisual_char_const__ptr__int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 80 | 68 | -12 | `seed` |
| `0x165A50` | `0x208110` | `0x425858` | `uiVisualWithBlendColor__uiVisualWithBlendColor_char_const__ptr__int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 160 | 202 | +42 | `seed` |
| `0x165C10` | `0x2082E0` | `0x424A68` | `uiText__FileIO_datParser__ref` | 112 | 107 | -5 | `prop_round_1` |
| `0x165C80` | `0x208350` | `0x424B20` | `uiText__FileIO_datParser__ref` | 544 | 529 | -15 | `seed` |
| `0x165EC0` | `-` | `0x424640` | `uiText__internalInit_int` | 48 | 0 | +0 | `ps2_callgraph` |
| `0x166000` | `0x2086B0` | `0x424A38` | `uiText__SetScaleValues_float_float` | 32 | 36 | +4 | `seed` |
| `0x166020` | `0x2086E0` | `0x424570` | `uiText__uiText_char_const__ptr__int_int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 160 | 211 | +51 | `seed` |
| `0x1665F0` | `0x209990` | `0x41EE10` | `uiDynamicText__InternalInit_char_const__ptr` | 224 | 218 | -6 | `seed` |
| `0x166740` | `0x209AE0` | `0x41EC98` | `uiDynamicText__uiDynamicText_char_const__ptr__int_int_int_char_const__ptr__int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 96 | 89 | -7 | `seed` |
| `0x1667A0` | `0x209B40` | `-` | `uiDynamicText__uiDynamicText_int_int_int_char_const__ptr__int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 96 | 96 | +0 | `insn_signature` |
| `0x166C30` | `0x2078B0` | `-` | `uiTranslatedText__uiTranslatedText_char_const__ptr__char_const__ptr__int_int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 80 | 80 | +0 | `prop_round_1` |
| `0x167410` | `0x209000` | `-` | `uiTable__uiTable_char_const__ptr__int_int_int_int_atDerivedPtr_uiMaster_atPtr_uiWidget_const__ref` | 160 | 159 | -1 | `insn_signature` |
| `0x1675F0` | `-` | `0x424220` | `uiTable__ForceLayoutEvents_void` | 16 | 0 | +0 | `ps2_callgraph` |
| `0x167610` | `0x2091B0` | `0x424260` | `uiTable__FileIO_datParser__ref` | 608 | 607 | -1 | `seed` |
| `0x167E70` | `0x20AAB0` | `0x41FC28` | `uiImageBase__BuildFullFileName_char__ptr__int_char_const__ptr__char_const__ptr` | 128 | 122 | -6 | `seed` |
| `0x168C30` | `-` | `0x422F70` | `uiCopyingString__Set_char_const__ptr__int` | 224 | 0 | +0 | `ps2_callgraph` |
| `0x168D10` | `-` | `0x423090` | `uiCopyingString__SetAlreadyAllocated_char_const__ptr` | 64 | 0 | +0 | `ps2_callgraph` |
| `0x178980` | `0x1B3B90` | `0x3B14D0` | `__builtin_new` | 48 | 110 | +62 | `seed` |
| `0x1789B0` | `0x1B3C00` | `0x3B1588` | `__builtin_delete` | 48 | 82 | +34 | `seed` |
| `0x178A10` | `0x26D820` | `0x3B16E8` | `__builtin_vec_delete` | 48 | 144 | +96 | `seed` |
| `0x1DF400` | `0x0EAE40` | `-` | `txtFontTex__Draw_float_float_unsigned_wchar_t_const__ptr__float_float_txtCursor__ptr__bool_txtDrawBuffer__ptr` | 381 | 2878 | +2497 | `prop_round_1` |
| `0x1E1900` | `0x360D20` | `0x5A0070` | `txtMovieSubtitles__SetupSubtitles_char_const__ptr` | 1360 | 987 | -373 | `seed` |
| `0x1E1E60` | `0x361370` | `0x5A0678` | `txtMovieSubtitles__FileIO_datParser__ref` | 96 | 88 | -8 | `seed` |
| `0x1EB6C0` | `0x189590` | `0x35F528` | `mcMenuRewardsScreen__LoadData_void` | 368 | 754 | +386 | `seed` |
| `0x1F2D60` | `0x2D88D0` | `0x526468` | `gfxLoadIpuImage_char_const__ptr` | 816 | 794 | -22 | `seed` |
| `0x1FA100` | `0x2B5E10` | `0x4FD740` | `huft_build_unsigned_int__ptr__unsigned_int_unsigned_int_unsigned_int_const__ptr__unsigned_int_const__ptr__inflate_huft_s__ptr__ptr__unsigned_int__ptr__inflate_huft_s__ptr__unsigned_int__ptr__unsigned_int__ptr` | 1264 | 1256 | -8 | `seed` |
| `0x1FB5D0` | `0x341020` | `0x5786A0` | `atReferenceCounter__atReferenceCounter_void` | 16 | 16 | +0 | `seed` |
| `0x2CD76E` | `0x3C06DC` | `-` | `XDK::IDirectSoundBuffer_Release` | 22 | 22 | +0 | `insn_signature` |
| `0x2CE348` | `0x3C140C` | `-` | `XDK::CDirectSoundStream_Discontinuity` | 77 | 77 | +0 | `insn_signature` |
| `0x2CEC93` | `0x3C1FC7` | `-` | `XDK::IDirectSound_DownloadEffectsImage` | 39 | 39 | +0 | `insn_signature` |
| `0x2CECBA` | `0x3C1FEE` | `-` | `XDK::IDirectSound_SetEffectData` | 42 | 42 | +0 | `insn_signature` |
| `0x2CEE37` | `0x3C215C` | `-` | `XDK::IDirectSoundBuffer_Stop` | 24 | 24 | +0 | `insn_signature` |
| `0x2CEEEB` | `0x3C2210` | `-` | `XDK::IDirectSoundBuffer_Lock` | 48 | 48 | +0 | `insn_signature` |
