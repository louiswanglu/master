// Foreground-instance matte using VNGenerateForegroundInstanceMaskRequest (macOS 14+).
// Produces a crisp per-instance alpha that separates the person from the chair,
// unlike the person-segmentation request which merges adjacent dark objects.
// usage: fgmask <input.png> <mask_out.png>

import Foundation
import Vision
import CoreImage
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func loadCGImage(_ path: String) -> CGImage {
    guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
          let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        FileHandle.standardError.write("cannot read \(path)\n".data(using: .utf8)!)
        exit(2)
    }
    return img
}

func savePNG(_ img: CGImage, _ path: String) {
    guard let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL,
                                                     UTType.png.identifier as CFString, 1, nil) else {
        FileHandle.standardError.write("cannot write \(path)\n".data(using: .utf8)!)
        exit(3)
    }
    CGImageDestinationAddImage(dest, img, nil)
    CGImageDestinationFinalize(dest)
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write("usage: fgmask in.png mask_out.png\n".data(using: .utf8)!)
    exit(1)
}
let inPath = args[1], maskPath = args[2]
let cg = loadCGImage(inPath)
let w = cg.width, h = cg.height
print("input \(w)x\(h)")

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([req]) } catch {
    FileHandle.standardError.write("vision error: \(error)\n".data(using: .utf8)!)
    exit(4)
}
guard let obs = req.results?.first else {
    FileHandle.standardError.write("no foreground observation\n".data(using: .utf8)!)
    exit(5)
}
print("instances: \(obs.allInstances.count)")

let ciCtx = CIContext(options: [.workingColorSpace: NSNull()])
do {
    let pb = try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
    let ci = CIImage(cvPixelBuffer: pb)
    let sx = CGFloat(w) / ci.extent.width
    let sy = CGFloat(h) / ci.extent.height
    let scaled = ci.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
    guard let maskCG = ciCtx.createCGImage(scaled, from: CGRect(x: 0, y: 0, width: w, height: h),
                                           format: .L8, colorSpace: CGColorSpaceCreateDeviceGray()) else {
        FileHandle.standardError.write("mask render failed\n".data(using: .utf8)!)
        exit(6)
    }
    savePNG(maskCG, maskPath)
    print("mask saved \(maskCG.width)x\(maskCG.height)")
} catch {
    FileHandle.standardError.write("mask error: \(error)\n".data(using: .utf8)!)
    exit(7)
}
