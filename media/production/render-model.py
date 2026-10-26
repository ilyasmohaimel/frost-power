"""Render a fresh, short camera move from an existing local G513QY studio model.
Supply FROST_MODEL_FILE. No personal imagery or scene file is exported.
"""
import os,bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];work=R/'media/work';work.mkdir(parents=True,exist_ok=True)
model=Path(os.environ['FROST_MODEL_FILE']);bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.eevee.use_raytracing=False
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=60;s.render.threads_mode='FIXED';s.render.threads=3
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15
screen=bpy.data.objects['Hyprland screen recording'];material=screen.data.materials[0];nodes=material.node_tree.nodes;tex=next(n for n in nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(R/'media/composition/assets/measurement-screen.png'),check_existing=False)
em=next(n for n in nodes if n.type=='EMISSION');material.node_tree.links.new(tex.outputs['Color'],em.inputs[0]);em.inputs['Strength'].default_value=.9
cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.dof.use_dof=False
# Same continuous fifth-order easing as the referenced daily-use revision.
# Sampling transforms per frame avoids integer crop steps and keeps velocity
# and acceleration at zero at the ends of each camera move.
wide=Vector((.45,-1.22,.82));hero=Vector((.035,-.72,.38))
wide_target=Vector((0,.055,.2));hero_target=Vector((0,.245,.285))
for frame in range(1,241):
 u=max(0,min(1,(frame-61)/179));e=u*u*u*(10-15*u+6*u*u)
 position=wide.lerp(hero,e);target=wide_target.lerp(hero_target,e)
 s.frame_set(frame);cam.location=position;cam.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();cam.data.lens=42+8*e
 cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame);cam.data.keyframe_insert('lens',frame=frame)
s.frame_start=1;s.frame_end=240;s.render.filepath=str(work/'model-frames/frame-');(work/'model-frames').mkdir(exist_ok=True)
if os.environ.get('FROST_PROOF_ONLY')=='1':
 s.frame_set(1);s.render.filepath=str(work/'model-proof.png');bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
import gpu
print('RENDER_DEVICE',gpu.platform.renderer_get(),flush=True)
