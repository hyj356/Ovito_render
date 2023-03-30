from ovito.io import import_file
from ovito.vis import TachyonRenderer as TR, OSPRayRenderer as OSPR
from ovito.vis import Viewport
import os
import glob

# 私有函数, 用于检查输入变量size是否符合规范
def __check_size(size):
  '''
  此函数为私有函数, 用于检查输入的参数size是否是一个长度为2的元组, 
  且元组里面的元素是否为2个正整数
  '''
  if len(size) != 2:
    raise ValueError("Input 'size' should contain exactly 2 elements.")
  if not isinstance(size[0], int) or not isinstance(size[1], int):
    raise TypeError("Elements in input 'size' should be integers.")
  if size[0] <= 1 or size[1] <= 1:
    raise ValueError("Elements in input 'size' should be positive integers.")

# 私有函数, 用于检查输入变量backcolor是否符合规范
def __check_backcolor(backcolor):
  '''
  此函数为私有函数, 用于检查输入的参数backcolor是否是一个长度为3的元组, 
  且元组里面的元素是否为一个在0-1之间的数字
  '''
  if len(backcolor) != 3:
    raise ValueError("Input 'backcolor' should contain exactly 3 elements.")
  for i in range(3):
    if not isinstance(backcolor[i], float) or backcolor[i] < 0 or backcolor[i] > 1:
      raise ValueError("Elements in input 'backcolor' should be floats between 0 and 1.")
    
# 私有函数, 用于检查输入的渲染器是否是OVITO中支持的渲染器
def __check_rend(rend):
  '''
  此函数为私有函数, 用于检查输入的参数rend是否是一个字符串, 
  且字符串内容是否符合要求
  '''
  if not isinstance(rend, str):
    raise TypeError("The argument rend must be a string!")
  
  rend_dict={
    'TR': 2,
    'OSPR': 3
  }
  result = rend_dict.get(rend, 0)

  if result == 0:
    raise TypeError("The render input are not supported in \
                    OVITO! Only 'TR' and 'OSPR are supported'")
  else:
    return result

def __check_cameraDir(cameraDir):
  '''
  此函数为私有函数, 用于检查输入的参数是否是一个长度为3的元组, 且元组里面的元素是否为数字
  '''
  if len(cameraDir) != 3:
    raise ValueError("Input 'cameraDir' should contain exactly 3 elements.")
  else:
    for item in cameraDir:
      if not isinstance(item, (int, float)):
        raise TypeError("Elements in input 'cameraDir' should be a number.")
# 在python中, 如果一个函数中的参数被设置了默认值, 比如设置a=1, 那么如果
# 在使用这个函数的时候命令a='1', 虽然传入的是字符串, 但是和默认值类型不一致
# python会放弃错误的传入参数, 转而使用函数定义的时候的默认值, 所以在运行的
# 时候并不会给出报错

def __check_cameraPos(cameraPos):
  '''
  此函数为私有函数, 用于检查输入的参数是否是一个长度为3的元组, 且元组里面的元素是否为数字
  '''
  if len(cameraPos) != 3:
    raise ValueError("Input 'cameraDir' should contain exactly 3 elements.")
  else:
    for item in cameraPos:
      if not isinstance(item, (int, float)):
        raise TypeError("Elements in input 'cameraDir' should be a number.")

def __check_filename(filename):
  '''
  私有函数, 用来判断输入的filename是否存在
  '''
  if '*' in filename:
    # 使用glob模块检查是否符合某一种格式的文件
    if not glob.glob(filename):
      raise FileNotFoundError(f"The file in the format {filename} \
                              was not found in the specified path.")
  else:
    if not os.path.exists(filename):
      raise FileNotFoundError(f'File {filename} not found in the \
                              currently specified path')

def __check_modifiers(modifiers):
  if not isinstance(modifiers, tuple):
    raise TypeError("The type of variable 'modifiers' must be a tuple!")
  else:
    if len(modifiers) == 0:
      raise ValueError("Must contains at least one element in variable 'modifiers'")

def __check_Fov(Fov):
  '''
  私有函数, 检查传入的参数Fov是否符合规范, Fov应该是一个大于0的数值
  '''
  if Fov < 0.0:
    raise ValueError("The value of variable 'Fov' must be a positive number!")

def export_png(fileName, outputName, renderPara, 
               size=(800, 600), isCell=False, frame=0,
               backcolor=(1.0, 1.0, 1.0), rend='TR',
               cameraDir=(2, 1, -1), cameraPos=[0, 0, 0],
               modifiers=None, Fov=100
               ):
  '''
  此函数用于将文件导入到OVITO中并导出相关图片处理, 但是具有一定限制, 比如OVITO出图
  的时候可以选择在图片中添加坐标轴, color lengend和text label, 但是由于涉及QT模块的
  调用问题, 总是无法运行成功, 所以暂时不加入类似的功能.输入的各参数的物理意义如下:
  fileName  : 字符串类型, 指定原子模型文件的名称, 如果文件名称是如"deform_*.xyz", 
  那么OVITO会自动把*替换为数字,并在对应的目录下面寻找所有符合条件的文件名并将其导入.
  outputName: 字符串类型, 输出的PNG图片的名字
  renderparameter: 字典类型, 渲染器在渲染时候需要使用和调整的参数
  size      : 元组类型, 里面有2个整数, 代表输出图片的长和宽, 默认为(800, 600)
  isCell    : 逻辑类型, 是否在输出的图片里面保留simulation cell的线框, 默认为False
  frame     : 对第几帧的文件进行渲染, 默认为第0帧
  backcolor : 元组类型, 使用RGB数组指定输出图片的背景颜色, 其值应该在[0, 1], 默认为(1, 1, 1)白色
  rend      : 字符串类型, OVITO中的渲染器类型, 可以选择的类型有TR(TachyonRenderer)和
  OSPR(OSPRayRenderer), OpenGL由于使用之前需要设置环境变量, 使用较为麻烦, 而且在免费
  的OVITO中也能使用, 所以不提供相关选项
  cameraDir : 元组类型, 里面有3个数字, 代表摄像头的视线方向, 默认为(2, 1, -1)
  cameraPos : 列表类型, 里面有3个数字, 代表摄像头的位置, 默认为盒子的xyz边长的一半
  Fov       : 对应OVITO中的field of view, 可以简单理解为将图像放大到多少倍
  modifiers : 元组类型, 内部可以包含N个OVITO提供的modifier, 用户可以在主程序中通过从
  ovito中的modifier模块导入需要的分析命令, 输入必要的参数, 然后将所有的模板传入这个函数中,
  以获得更好的渲染效果, 同时也需要注意各个modifier的顺序先后问题.
  '''
  
  # 检查输入参数是否符合规范
  __check_filename(fileName)
  __check_size(size)
  __check_backcolor(backcolor)
  renders = __check_rend(rend)
  __check_cameraDir(cameraDir)
  __check_cameraPos(cameraPos)
  __check_Fov(Fov)

  # 然后我们导入模型
  pipeline = import_file(fileName)

  # 检测用户是否提供了modifier, 如果提供了将其添加进去并进行计算
  if modifiers != None:
    __check_modifiers(modifiers)
    for item in modifiers:
      pipeline.modifiers.append(item)
    pipeline.compute()

  # 获取一共有多少帧文件
  totalFrame = pipeline.source.num_frames

  # 将模型添加进场景
  pipeline.add_to_scene()

  # 如果要求在图片中渲染simulation cell, 就给他渲染
  pipeline.source.data.cell.vis.render_cell= True if isCell else False

  # 获取一些参数
  lx = pipeline.compute().cell[0, 0]    # 盒子在x方向上的长度
  ly = pipeline.compute().cell[1, 1]    # 盒子在x方向上的长度
  lz = pipeline.compute().cell[2, 2]    # 盒子在x方向上的长度

  # 选择摄像机的角度和位置, 这里可以预先在OVITO里面调整好之后再将数据输入到代码中
  if (cameraPos == [0,0,0]):    # 如果用户没有手动定义摄像机位置, 就选择默认的位置
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=cameraDir, 
                camera_pos=[lx/2, ly/2, lz/2], fov=Fov)
  else:
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=cameraDir, 
                camera_pos=cameraPos, fov=Fov)
  
  # 正式开始渲染
  if renders == 2:
    # 这里对应的是使用TachyonRenderer渲染器
    vp.render_image(size=size, filename=outputName, 
                  background=backcolor, frame=frame,
                  renderer=TR(
                  ambient_occlusion = renderPara['ambient_occlusion'],
                  ambient_occlusion_brightness = renderPara['ambient_occlusion_brightness'],
                  ambient_occlusion_samples = renderPara['ambient_occlusion_samples'],
                  antialiasing = renderPara['antialiasing'],
                  antialiasing_samples = renderPara['antialiasing_samples'],
                  aperture = renderPara['aperture'],
                  depth_of_field = renderPara['depth_of_field'],
                  direct_light = renderPara['direct_light'],
                  direct_light_intensity = renderPara['direct_light_intensity'],
                  focal_length = renderPara['focal_length'],
                  shadows = renderPara['shadows']
                  ))
    
    # 输出相关信息到屏幕上面, 这里注意使用了f-string语法, 
    # 此功能在python3.6之后才正式支持
    print(f"A total of {totalFrame} frames were found, and frame {frame} \
is now being rendered using TachyonRenderer. \n \
The position of camera is {[lx/2, ly/2, lz/2]}, \n\
and the direction of camera is {cameraDir}")
    
    # 渲染完成之后清除所有的场景, 这个步骤是必要的, 否则如果多次调用这个函数,
    # 那么上一次函数的相关设置就可能会影响下一次图片的渲染
    pipeline.remove_from_scene()
  
  elif renders == 3:
    # 这里对应使用的是OSPRayRenderer渲染器
    vp.render_image(size=size, filename=outputName, 
        background=backcolor, frame=frame,
        renderer=OSPR(
        ambient_brightness = renderPara['ambient_brightness'],
        ambient_light_enabled = renderPara['ambient_light_enabled'],
        aperture = renderPara['aperture'],
        denoising_enabled = renderPara['denoising_enabled'],
        direct_light_angular_diameter = renderPara['direct_light_angular_diameter'],
        direct_light_enabled = renderPara['direct_light_enabled'],
        direct_light_intensity = renderPara['direct_light_intensity'],
        dof_enabled = renderPara['dof_enabled'],
        focal_length = renderPara['focal_length'],
        material_shininess = renderPara['material_shininess'],
        material_specular_brightness = renderPara['material_specular_brightness'],
        max_ray_recursion = renderPara['max_ray_recursion'],
        refinement_iterations = renderPara['refinement_iterations'],
        samples_per_pixel = renderPara['samples_per_pixel'],
        sky_albedo = renderPara['sky_albedo'],
        sky_brightness = renderPara['sky_brightness'],
        sky_light_enabled = renderPara['sky_light_enabled'],
        sky_turbidity = renderPara['sky_turbidity']
    ))
    # 输出相关信息到屏幕上面, 这里注意使用了f-string语法, 
    # 此功能在python3.6之后才正式支持
    print(f"A total of {totalFrame} frames were found, and frame {frame} \
is now being rendered using OSPRayRenderer. \n \
The position of camera is {[lx/2, ly/2, lz/2]}, \n\
and the direction of camera is {cameraDir}")
    # 渲染完成之后清除所有的场景, 这个步骤是必要的, 否则如果多次调用这个函数,
    # 那么上一次函数的相关设置就可能会影响下一次图片的渲染
    pipeline.remove_from_scene()
