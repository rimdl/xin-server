from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string

def generate_random_string(length=6, characters=string.ascii_letters + string.digits):
    """生成指定长度的随机字符串"""
    return ''.join(random.choice(characters) for _ in range(length))

def create_captcha_image(code, font_path='../font.ttf', width=550, height=200, char_spacing=1.5, background_color=(255, 255, 255)):
    """生成包含指定验证码的图片"""

    # 创建空白图像
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 选择字体
    font_size = int(height * 0.8)
    font = ImageFont.truetype(font_path, font_size)

    # 计算每个字符的位置
    char_box = font.getbbox('A')  # 获取单个字符宽度作为参考
    char_width = char_box[2]-char_box[0]
    total_char_width = len(code) * char_width * char_spacing
    x_offset = (width - total_char_width) / 2

    # 绘制字符
    for char, i in zip(code, range(len(code))):
        draw.text((x_offset + i * (char_width * char_spacing), 0), char, font=font, fill=(0, 0, 0))

    # 添加随机噪声线
    for _ in range(100):
        line_color = tuple(random.randint(0, 255) for _ in range(3))
        draw.line([(random.randint(0, width), random.randint(0, height)),
                   (random.randint(0, width), random.randint(0, height))], fill=line_color, width=random.randint(1, 3))

    # 添加随机噪声点
    for _ in range(50):
        point_color = tuple(random.randint(0, 255) for _ in range(3))
        draw.point([random.randint(0, width), random.randint(0, height)], fill=point_color)

    # 应用模糊滤镜以增加噪声
    image = image.filter(ImageFilter.BLUR)
    return image

