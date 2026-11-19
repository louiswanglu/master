# 证件照（1 寸 / 2 寸）

| 文件 | 尺寸 | 大小 | 说明 |
|---|---|---|---|
| `idphoto_2inch_1200x1680.jpg` | 1200×1680（300 dpi，5:7） | 约 317 KB | 高清交付版 |
| `idphoto_1inch_413x579.jpg` | 413×579（300 dpi，5:7） | 约 65 KB | 标准 1 寸 |

## 对应规则

1. 彩色、近期、半身：保留原始彩色，仅做轻度影棚调色（无滤镜感）
2. 背景纯白：合成后背景像素实测为 `(255,255,255)`
3. 免冠正脸、无配饰：原图本身无帽子/眼镜/耳机/围巾
4. 表情自然：保留原神情，未做表情修改
5. 只有本人：椅子、书架、绿植全部去除
6. 格式 JPG
7. 文件均小于 1 MB

## 处理流程

原图是在办公椅上（背景书架）拍的，Vision 的人像/前景分割都会把深色椅背
粘到肩膀两侧，直接抠图会在白底上留下灰色残块。因此：

- **肩线**：针织衫是全画面唯一偏蓝的材质（B-R 达 +60，椅子仅 0~10），
  逐列取「连续蓝色针织」的最高行 → 滚动取极大值去掉领口凹陷 → 两次平滑，
  得到一条干净肩线；椅背在肩线之上，天然被排除。
- **头部/耳朵**：Vision 实例分割在该区域质量很好，只用脸部椭圆约束。
- **颈部**：逐行取穿过面部中轴的暖色肤色（R-B > 6）连续段，再按行亮度裁掉
  阴影过渡带，最后在颈部区间做加宽平滑；这样颈部边缘落在亮部肤色上，
  不会留黑边，也带上了下巴底下的阴影。
- **收尾**：只保留含脸部的连通域并填洞；边缘阴影用「比邻域显著更暗」判据
  在轮廓带内回收；按预乘 alpha 上采样，避免深色头发在缩放时被白底污染出
  灰边；合成到纯白后做轻度 USM 锐化，JPEG（4:4:4，300 dpi）压在 1 MB 内。

## 重新生成

```bash
PY=/Users/wanglu/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

# 1) 人脸关键点 + Vision 前景蒙版（首次需编译 Swift 工具）
swiftc -O -module-cache-path /tmp/mc tools/faceinfo.swift -o tools/faceinfo
swiftc -O -module-cache-path /tmp/mc tools/fgmask.swift   -o tools/fgmask
./tools/faceinfo source.png > build/face.json
./tools/fgmask   source.png   build/fgmask.png

# 2) 剪影 → 成品
$PY tools/silhouette.py
$PY tools/build.py
```

`source.png` 是原始附件的无损副本；`build/` 里是中间产物。
