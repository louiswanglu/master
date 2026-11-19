// Dump face detection + landmark geometry as JSON.
// usage: faceinfo <input.png>
// Coordinates are in pixels, origin at top-left of the image (y grows downward).

import Foundation
import Vision
import CoreGraphics
import ImageIO

func loadCGImage(_ path: String) -> CGImage {
    let url = URL(fileURLWithPath: path)
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        FileHandle.standardError.write("cannot read \(path)\n".data(using: .utf8)!)
        exit(2)
    }
    return img
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    FileHandle.standardError.write("usage: faceinfo in.png\n".data(using: .utf8)!)
    exit(1)
}

let cg = loadCGImage(args[1])
let w = CGFloat(cg.width), h = CGFloat(cg.height)

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
let req = VNDetectFaceLandmarksRequest()
req.revision = VNDetectFaceLandmarksRequestRevision3

do { try handler.perform([req]) } catch {
    FileHandle.standardError.write("vision error: \(error)\n".data(using: .utf8)!)
    exit(3)
}

// Landmark normalizedPoints are relative to the FACE BOUNDING BOX (origin bottom-left),
// so map them through the bounding box into top-left pixel coordinates.
func px(_ p: CGPoint, _ bb: CGRect) -> [String: Double] {
    let nx = bb.minX + CGFloat(p.x) * bb.width
    let ny = bb.minY + CGFloat(p.y) * bb.height
    return ["x": Double(nx * w), "y": Double((1 - ny) * h)]
}

func points(_ region: VNFaceLandmarkRegion2D?, _ bb: CGRect) -> [[String: Double]] {
    guard let r = region else { return [] }
    return r.normalizedPoints.map { px($0, bb) }
}

var out: [String: Any] = ["imageWidth": Double(w), "imageHeight": Double(h), "faces": []]
var faces: [[String: Any]] = []

for f in (req.results ?? []) {
    let bb = f.boundingBox
    var entry: [String: Any] = [
        "confidence": Double(f.confidence),
        "bbox": [
            "x": Double(bb.minX * w),
            "y": Double((1 - bb.maxY) * h),
            "w": Double(bb.width * w),
            "h": Double(bb.height * h)
        ],
        "roll": Double(f.roll?.doubleValue ?? 0),
        "yaw": Double(f.yaw?.doubleValue ?? 0),
        "pitch": Double(f.pitch?.doubleValue ?? 0)
    ]
    if let lm = f.landmarks {
        entry["leftEye"] = points(lm.leftEye, bb)
        entry["rightEye"] = points(lm.rightEye, bb)
        entry["leftPupil"] = points(lm.leftPupil, bb)
        entry["rightPupil"] = points(lm.rightPupil, bb)
        entry["nose"] = points(lm.nose, bb)
        entry["noseCrest"] = points(lm.noseCrest, bb)
        entry["medianLine"] = points(lm.medianLine, bb)
        entry["outerLips"] = points(lm.outerLips, bb)
        entry["innerLips"] = points(lm.innerLips, bb)
        entry["faceContour"] = points(lm.faceContour, bb)
        entry["leftEyebrow"] = points(lm.leftEyebrow, bb)
        entry["rightEyebrow"] = points(lm.rightEyebrow, bb)
    }
    faces.append(entry)
}
out["faces"] = faces

let data = try! JSONSerialization.data(withJSONObject: out, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write("\n".data(using: .utf8)!)
