/**
 * @typedef {'fast' | 'high_accuracy'} CameraOcrMode
 */

/**
 * @typedef {'off' | 'grayscale' | 'bw_high_contrast'} CameraPreprocessMode
 */

/**
 * @typedef {{x:number,y:number,width:number,height:number}} CameraBBox
 */

/**
 * @typedef {{text:string,confidence:number|null,bbox:CameraBBox}} CameraOcrLine
 */

/**
 * @typedef {{
 * pageIndex:number,
 * text:string,
 * lines:CameraOcrLine[],
 * metrics:{
 * charCount:number,
 * alphaRatio:number,
 * meanConf:number|null,
 * lowConfFrac:number|null,
 * numLines:number,
 * medianTokenLen:number,
 * blurVariance?:number,
 * overexposureRatio?:number,
 * },
 * warnings?:string[],
 * }} CameraOcrPage
 */

/**
 * @typedef {{
 * pageIndex:number,
 * bitmap:ImageBitmap,
 * width:number,
 * height:number,
 * previewUrl?:string,
 * }} CapturedCameraPage
 */

export const CAMERA_TYPES = Object.freeze({
  OCR_RUN: "camera_ocr_run",
  OCR_CANCEL: "camera_ocr_cancel",
  OCR_PROGRESS: "camera_ocr_progress",
  OCR_PAGE: "camera_ocr_page",
  OCR_DONE: "camera_ocr_done",
  OCR_ERROR: "camera_ocr_error",
  OCR_CANCELLED: "camera_ocr_cancelled",
});
