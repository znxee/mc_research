# Vehicle assembly source notes (read-only research)

- Canonical existing toolkit assembly oracle: mc3_traffic_mlod.build_lod/_stock_pieces.
- More precise static bind pose than its translation-only bake: alpha crSkeleton::Init 0x547A08 initializes local Euler XYZ at node+0x2C and local translation node+0x20; crSkeleton::Update 0x547BB0 composes parent matrices in order. Matrix34::FromEulersXYZ 0x236738 supplies rotation formula. Node+0 is serialized absolute position; validated against composed local hierarchy (tolerance1e-4).
- Main vehicle body+8 -> rmcCarModelType; +D8 -> drwShaderModel; +DC -> crSkeletonData; +328 duplicate skeletoncount. drwShaderModel+10 -> HLOD.
- mcCarModelType AddNamesToPartDatabase retail0x302D10 establishes customization arrays/counts in canonical Documentation/MC3_VEHICLE_RAM.md. Read CarCfg index, selected arrayID; HLOD matches skeletonID, nullmesh loads exact HLODname+'.pck'. External standalone materialindices refer to parentvehicle group.
- 350Z defaults all selections0: frontbumper75, rear113, skirts53, spoiler19, hood41, taillight178. Main HLOD embedded suspensionarms2/3/4/5, trunk16(2meshes), body0(4meshes),neon15. NeonIdx0 omitsneon.
- Wheels toolkit mc3_traffic_wheels.stock_setup,ppf_model,model_geometry,wheel_mesh. CarCfg rim136->whl_rm_350z_04 page143, tire0->whl_tir_bfghrch_blk page0 (multiple pages reuse black tire names; explicit0).
- pf05 descriptor (entry&0x7FFFF)*0x800, (entry>>19)*0x400. Modelchunk kindFFFF0000,32byte header, VA@0, length@12. Payload drwShaderModel includes shadergroup+8, MLOD+14. Native temporary-memory PCKheader128+payload preservesoriginalVA.
- Wheel width [.195,.215,.235,.255,.275,.295,.315,.335,.355], profile ratios[.415532,.47585,.538852,.6,.66,.725,.782,.83]. Retail mcCarConfig::CalcTireWidth4AF890/GetRimScale4AFAB0; alpha GetDefaultTireDiameter2B6E68 and retail2CA780 = twice stockwheelrecordY.
- Scale X=2*width, radial=diameter*(rimratio or1); rightside rotateY(pi), never mirrorXalone. Tireinnerbaseprofile ring scales additionally ratio/.415532 to matchselectedrim. This matches canonical traffic wheel prebake.
- Limits: profile-1 automatic unsupported; camber/rideheight/offset/dynamic suspension/rotation excluded in first static assembly; floating wheel blur shader omitted; no playercar wheel shader equivalence claim.
- First compile exposed suspension constant-CPV stream with STMASK55555555+STROW[127,127,127,0], filling STCYCL CL1/WLvertexcount and masked V4-8 consumingonevector. Sent exact layout to root to extend nativeVIF safely.

Ignored structure/wheel JSON reports contain original asset metadata. No originals changed.
