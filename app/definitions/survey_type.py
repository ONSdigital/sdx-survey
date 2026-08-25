from enum import StrEnum


class SurveyType(StrEnum):
    EQV1JSON = "eqv1json"
    SPPJSON_IMG_RCPT = "sppjson_img_rcpt"
    EQV1JSON_IMG_RCPT = "eqv1json_img_rcpt"
    EQV2JSON_IMG_RCPT = "eqv2json_img_rcpt"
    FEEDBACK = "feedback"
    EQV2JSON = "eqv2json"
    PCK_IMG_RCPT = "pck_img_rcpt"
    PCK = "pck"
    PCK_IMG = "pck_img"
