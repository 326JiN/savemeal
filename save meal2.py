from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import time
from typing import Any
import unicodedata

from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent
CONTROLS_DIR = APP_DIR / "components" / "cooking_controls"

CONTROLS_COMPONENT: Any = (
    components.declare_component("savemeal_cooking_controls", path=str(CONTROLS_DIR))
    if CONTROLS_DIR.exists()
    else None
)


@dataclass(frozen=True)
class Step:
    title: str
    minutes: int
    instruction: str
    voice: str
    microwave_minutes_700w: int | None = None
    microwave_minutes_1000w: int | None = None


@dataclass(frozen=True)
class Recipe:
    folder: str
    title: str
    total_minutes: int
    ingredients: tuple[str, ...]
    ingredient_tags: tuple[str, ...]
    steps: tuple[Step, ...]
    sources: tuple[str, ...]
    variant: str = "B"


DELIVERY_FEE = 3_000

UNIT_PRICES: dict[str, float] = {
    "밥": 2133 / 210,
    "신김치": 29206 / 2600,
    "스팸": 5323 / 200,
    "계란": 9527 / 15,
    "식용유": 4890 / 900,
    "참기름": 12936 / 320,
    "돼지고기": 4056 / 100,
    "두부": 4107 / 380,
    "대파": 2892 / 650,
    "고춧가루": 15380 / 200,
    "다진마늘": 1894 / 100,
    "간장": 7942 / 860,
    "참치캔": 3620 / 150,
    "마요네즈": 7295 / 500,
    "양파": 3562 / 1500,
    "고추장": 16859 / 1000,
    "설탕": 2395 / 1000,
    "소면": 4471 / 900,
    "식초": 3896 / 900,
}

RECIPE_COST_USAGE: dict[str, dict[str, tuple[float, str]]] = {
    "김치스팸볶음밥": {
        "밥": (200, "g"),
        "신김치": (100, "g"),
        "스팸": (67, "g"),
        "계란": (1, "개"),
        "식용유": (30, "ml"),
        "참기름": (7.5, "ml"),
    },
    "김치찌개": {
        "신김치": (100, "g"),
        "돼지고기": (100, "g"),
        "두부": (150, "g"),
        "대파": (25, "g"),
        "고춧가루": (7, "g"),
        "다진마늘": (7, "g"),
        "간장": (15, "ml"),
        "식용유": (15, "ml"),
        "물": (360, "ml"),
    },
    "참치마요덮밥": {
        "밥": (200, "g"),
        "참치캔": (100, "g"),
        "마요네즈": (30, "g"),
        "계란": (2, "개"),
        "식용유": (7.5, "ml"),
    },
    "제육볶음덮밥": {
        "밥": (200, "g"),
        "돼지고기": (150, "g"),
        "양파": (50, "g"),
        "대파": (25, "g"),
        "식용유": (15, "ml"),
        "고추장": (30, "g"),
        "간장": (15, "ml"),
        "설탕": (12, "g"),
        "다진마늘": (7, "g"),
    },
    "비빔국수": {
        "소면": (100, "g"),
        "신김치": (50, "g"),
        "고추장": (30, "g"),
        "설탕": (6, "g"),
        "식초": (7.5, "ml"),
        "참기름": (7.5, "ml"),
        "물": (720, "ml"),
    },
}

DELIVERY_PRICES: dict[str, int] = {
    "김치스팸볶음밥": 5200,
    "김치찌개": 6000,
    "참치마요덮밥": 3800,
    "제육볶음덮밥": 6500,
    "비빔국수": 6900,
}


def calculate_savings(menu_name: str) -> dict[str, int] | None:
    usage_map = RECIPE_COST_USAGE.get(menu_name)
    delivery_price = DELIVERY_PRICES.get(menu_name)
    if not usage_map or delivery_price is None:
        return None

    cost = sum(
        (Decimal(str(usage)) * Decimal(str(UNIT_PRICES.get(ingredient, 0)))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for ingredient, (usage, _unit) in usage_map.items()
    )
    ingredient_cost = int(round(cost))
    delivery_total = delivery_price + DELIVERY_FEE
    return {
        "ingredient_cost": ingredient_cost,
        "delivery_price": delivery_price,
        "delivery_fee": DELIVERY_FEE,
        "delivery_total": delivery_total,
        "savings": delivery_total - ingredient_cost,
    }


RECIPES: tuple[Recipe, ...] = (
    Recipe(
        folder="김치스팸볶음밥",
        title="김치스팸볶음밥",
        total_minutes=12,
        ingredients=(
            "찬밥 종이컵 1컵 반",
            "신김치 종이컵 1컵",
            "스팸 종이컵 ½컵",
            "계란 1개",
            "식용유 2숟가락",
            "참기름 ½숟가락",
            "선택 재료 설탕 ½숟가락",
        ),
        ingredient_tags=("밥", "김치", "스팸", "계란"),
        steps=(
            Step(
                "재료 썰기",
                3,
                "김치 종이컵 1컵은 가위로 1cm 폭으로 자르고, 스팸 종이컵 ½컵은 새끼손톱 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요.",
                "일 단계, 재료 썰기. 김치는 가위로 일 센티미터 폭으로 자르고 스팸은 새끼손톱 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요.",
            ),
            Step(
                "계란 부치기",
                2,
                "중불에 식용유 1숟가락을 두르고 계란 1개를 흰자가 익을 때까지 부쳐 접시에 옮겨 주세요. 기름이 튀니 얼굴을 팬에서 떼세요.",
                "이 단계, 계란 부치기. 중불에 식용유 한 숟가락을 두르고 계란을 흰자가 하얗게 굳을 때까지 부쳐 접시에 옮겨 주세요. 기름이 튀니 얼굴을 팬에서 떼세요.",
            ),
            Step(
                "스팸 볶기",
                2,
                "중불에 식용유 1숟가락을 두르고 스팸을 겉이 노릇해질 때까지 볶아 주세요.",
                "삼 단계, 스팸 볶기. 같은 팬에 식용유 한 숟가락을 두르고 스팸을 겉이 노릇해질 때까지 볶아 주세요.",
            ),
            Step(
                "김치 볶기",
                2,
                "중불에서 김치를 넣고 숨이 죽을 때까지 볶아 주세요. 많이 시면 설탕 ½숟가락을 넣으세요.",
                "사 단계, 김치 볶기. 중불 그대로 김치를 넣고 숨이 죽을 때까지 볶아 주세요. 김치가 많이 시면 설탕 반 숟가락을 넣으세요.",
            ),
            Step(
                "밥 볶기",
                3,
                "약불로 줄이고 찬밥 종이컵 1컵 반을 넣어 덩어리를 풀며 볶아 주세요. 불을 끄고 참기름 ½숟가락을 두른 뒤 계란을 올리세요.",
                "오 단계, 밥 볶기. 약불로 줄이고 찬밥을 넣어 덩어리를 풀며 볶아 주세요. 불을 끄고 참기름 반 숟가락을 두른 뒤 계란을 올리면 완성이에요.",
            ),
        ),
        sources=(
            "써지니, 만개의레시피, https://www.10000recipe.com/recipe/7021642",
            "hancy002, 만개의레시피, https://www.10000recipe.com/recipe/6908421",
        ),
    ),
    Recipe(
        folder="김치찌개",
        title="김치찌개",
        total_minutes=22,
        ingredients=(
            "신김치 종이컵 1컵",
            "돼지고기 목살 종이컵 1컵",
            "물 종이컵 2컵",
            "대파 ¼대",
            "고춧가루 1숟가락",
            "다진마늘 ½숟가락",
            "국간장 1숟가락",
            "식용유 1숟가락",
            "선택 재료 두부 ½모",
            "선택 재료 설탕 ½숟가락",
        ),
        ingredient_tags=("김치", "돼지고기", "대파", "두부"),
        steps=(
            Step(
                "재료 썰기",
                3,
                "김치 종이컵 1컵은 가위로 2cm 폭으로 자르고 목살 종이컵 1컵은 한입 크기로 썰어 주세요. 대파 ¼대와 선택한 두부도 썰고 칼날 반대쪽에 손가락을 두세요.",
                "일 단계, 재료 썰기. 김치는 가위로 이 센티미터 폭으로 자르고 목살은 한입 크기, 대파는 어슷하게 썰어 주세요. 칼날 반대쪽에 손가락을 두세요.",
            ),
            Step(
                "고기·김치 볶기",
                4,
                "중불에 식용유 1숟가락을 두르고 목살을 볶은 뒤 김치를 넣어 숨이 죽을 때까지 볶아 주세요. 많이 시면 설탕 ½숟가락을 넣으세요.",
                "이 단계, 고기와 김치 볶기. 중불에 식용유 한 숟가락을 두르고 목살을 겉면 색이 변할 때까지 볶은 뒤 김치를 넣어 숨이 죽을 때까지 볶아 주세요. 김치가 많이 시면 설탕 반 숟가락을 넣으세요.",
            ),
            Step(
                "물 붓고 끓이기",
                5,
                "물 종이컵 2컵을 붓고 강불에서 끓어오를 때까지 기다려 주세요. 끓는 국물이 튀니 얼굴을 냄비에서 떼세요.",
                "삼 단계, 물 붓고 끓이기. 물 두 컵을 붓고 강불에서 끓어오를 때까지 기다려 주세요. 국물이 튀니 얼굴을 떼세요.",
            ),
            Step(
                "양념 넣기",
                7,
                "중불로 줄이고 고춧가루 1숟가락, 다진마늘 ½숟가락, 국간장 1숟가락을 넣어 끓여 주세요.",
                "사 단계, 양념 넣기. 중불로 줄이고 고춧가루 한 숟가락, 다진마늘 반 숟가락, 국간장 한 숟가락을 넣어 칠 분 정도 끓여 주세요.",
            ),
            Step(
                "대파 넣고 마무리",
                3,
                "선택한 두부와 대파를 넣고 약불에서 3분 더 끓인 뒤 불을 꺼 주세요.",
                "오 단계, 대파 넣고 마무리. 두부와 대파를 넣고 약불에서 삼 분 정도 더 끓인 뒤 불을 꺼면 완성이에요.",
            ),
        ),
        sources=(
            "요리다나와, 만개의레시피, https://www.10000recipe.com/recipe/6920236",
            "달링제이, 만개의레시피, https://www.10000recipe.com/recipe/6994341",
        ),
    ),
    Recipe(
        folder="비빔국수",
        title="비빔국수",
        total_minutes=10,
        ingredients=(
            "소면 1인분",
            "신김치 종이컵 ½컵",
            "삶는 물 종이컵 4컵",
            "고추장 1½숟가락",
            "설탕 ½숟가락",
            "식초 ½숟가락",
            "참기름 ½숟가락",
        ),
        ingredient_tags=("김치", "소면"),
        steps=(
            Step(
                "김치 썰기",
                1,
                "김치 종이컵 ½컵을 가위로 잘게 잘라 주세요.",
                "일 단계, 김치 썰기. 김치를 가위로 잘게 잘라 주세요.",
            ),
            Step(
                "양념장 만들기",
                2,
                "고추장 1½숟가락, 설탕 ½숟가락, 식초 ½숟가락, 참기름 ½숟가락을 먼저 섞어 주세요.",
                "이 단계, 양념장 만들기. 고추장 한 숟가락 반, 설탕과 식초, 참기름을 반 숟가락씩 넣어 먼저 섞어 주세요.",
            ),
            Step(
                "면 삶기",
                4,
                "강불에서 소면을 삶고 끓어오를 때마다 찬물 ½컵씩 두 번 부은 뒤 세 번째에 불을 꺼 주세요. 면을 천천히 넣어 뜨거운 물이 튀지 않게 하세요.",
                "삼 단계, 면 삶기. 끓는 물에 소면을 천천히 넣고, 끓어오를 때마다 찬물 반 컵씩 두 번 부어 주세요. 세 번째로 끓으면 불을 끄세요.",
            ),
            Step(
                "면 헹구기",
                2,
                "면을 체에 쏟아 찬물에 비벼 헹군 뒤 물기를 털어 주세요. 뜨거운 김에 데지 않게 얼굴을 떼세요.",
                "사 단계, 면 헹구기. 면을 체에 쏟아 찬물에 비벼 헹구고 물기를 털어 주세요. 뜨거운 김을 조심하세요.",
            ),
            Step(
                "비비기",
                1,
                "양념장에 면과 김치를 넣고 고루 비벼 주세요.",
                "오 단계, 비비기. 양념장에 면과 김치를 넣고 고루 비비면 완성이에요.",
            ),
        ),
        sources=(
            "hancy002, 만개의레시피, https://www.10000recipe.com/recipe/6907160",
            "전라도언니루비씨, 만개의레시피, https://www.10000recipe.com/recipe/6853908",
        ),
    ),
    Recipe(
        folder="제육볶음",
        title="제육볶음덮밥",
        total_minutes=23,
        ingredients=(
            "밥 종이컵 1컵 반",
            "돼지고기 앞다리살 또는 목살 종이컵 2컵",
            "양파 ¼개",
            "대파 ¼대",
            "식용유 1숟가락",
            "고추장 1½숟가락",
            "간장 1숟가락",
            "설탕 1숟가락",
            "다진마늘 ½숟가락",
        ),
        ingredient_tags=("밥", "돼지고기", "양파", "대파"),
        steps=(
            Step(
                "재료 썰기",
                3,
                "양파 ¼개는 채 썰고 대파 ¼대는 어슷하게 썰어 주세요. 고기는 핏물을 닦아 한입 크기로 썰고 칼날 반대쪽에 손가락을 두세요.",
                "일 단계, 재료 썰기. 양파는 채 썰고 대파는 어슷하게, 고기는 핏물을 닦아 한입 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요.",
            ),
            Step(
                "고기 양념하기",
                12,
                "고추장 1½숟가락, 간장 1숟가락, 설탕 1숟가락, 다진마늘 ½숟가락을 섞어 고기를 버무리고 10분 두세요.",
                "이 단계, 고기 양념하기. 고추장 한 숟가락 반, 간장 한 숟가락, 설탕 한 숟가락, 다진마늘 반 숟가락을 섞고 고기를 고루 버무려 십 분 정도 두세요.",
            ),
            Step(
                "고기 볶기",
                5,
                "중불에 식용유 1숟가락을 두르고 고기를 분홍빛이 사라질 때까지 볶아 주세요. 양념이 타지 않게 계속 뒤적이세요.",
                "삼 단계, 고기 볶기. 중불에 식용유 한 숟가락을 두르고 고기를 분홍빛이 사라질 때까지 볶아 주세요. 양념이 타지 않게 계속 뒤적이세요.",
            ),
            Step(
                "채소 넣고 볶기",
                2,
                "양파를 넣어 숨이 죽을 때까지 볶고 대파를 넣어 섞은 뒤 불을 꺼 주세요.",
                "사 단계, 채소 넣고 볶기. 양파를 넣어 숨이 죽을 때까지 볶고 대파를 넣어 섞은 뒤 불을 꺼 주세요.",
            ),
            Step(
                "밥에 올리기",
                1,
                "그릇에 밥 종이컵 1컵 반을 담고 제육볶음을 올려 주세요.",
                "오 단계, 밥에 올리기. 그릇에 밥을 담고 제육볶음을 올리면 완성이에요.",
            ),
        ),
        sources=(
            "만개의레시피, https://www.10000recipe.com/recipe/6899190",
            "겨대생, 만개의레시피, https://www.10000recipe.com/recipe/6906467",
        ),
    ),
    Recipe(
        folder="참치마요덮밥",
        title="참치마요덮밥",
        total_minutes=7,
        ingredients=(
            "밥 종이컵 1컵 반",
            "참치캔 1개",
            "마요네즈 2숟가락",
            "계란 2개",
            "식용유 ½숟가락",
            "김가루 2숟가락",
        ),
        ingredient_tags=("밥", "참치", "계란"),
        steps=(
            Step(
                "참치 기름 빼기",
                1,
                "참치캔 기름을 숟가락으로 눌러 따라 버려 주세요. 캔 뚜껑 가장자리를 조심하세요.",
                "일 단계, 참치 기름 빼기. 참치캔 기름을 숟가락으로 눌러 따라 버려 주세요. 캔 뚜껑 가장자리는 날카로우니 조심하세요.",
            ),
            Step(
                "참치마요 만들기",
                2,
                "참치와 마요네즈 2숟가락을 고루 섞어 주세요.",
                "이 단계, 참치마요 만들기. 참치와 마요네즈 두 숟가락을 고루 섞어 주세요.",
            ),
            Step(
                "계란 스크램블",
                2,
                "중불에 식용유 ½숟가락을 두르고 계란 2개를 풀어 저으며 익혀 주세요.",
                "삼 단계, 계란 스크램블. 중불에 식용유 반 숟가락을 두르고 계란 두 개를 풀어 저으며 이 분 정도 몽글몽글 덩어리가 질 때까지 익혀 주세요.",
            ),
            Step(
                "밥 담기",
                1,
                "그릇에 밥 종이컵 1컵 반을 담고 스크램블을 올려 주세요.",
                "사 단계, 밥 담기. 그릇에 밥을 담고 스크램블을 올려 주세요.",
            ),
            Step(
                "참치마요 올리기",
                1,
                "스크램블 위에 참치마요를 올리고 김가루 2숟가락을 뿌려 주세요.",
                "오 단계, 참치마요 올리기. 참치마요를 올리고 김가루를 뿌리면 완성이에요.",
            ),
        ),
        sources=(
            "진니찡, 만개의레시피, https://www.10000recipe.com/recipe/6879335",
            "시크제이맘, 만개의레시피, https://www.10000recipe.com/recipe/6867725",
        ),
    ),
)

MICROWAVE_RECIPES: tuple[Recipe, ...] = (
    Recipe(
        folder="김치스팸볶음밥",
        title="김치스팸볶음밥",
        total_minutes=14,
        ingredients=("찬밥 1공기", "신김치 ½컵", "스팸 ⅓캔", "계란 1개", "식용유 1작은술", "참기름 1작은술"),
        ingredient_tags=("밥", "김치", "스팸", "계란"),
        steps=(
            Step("재료 손질", 2, "전자레인지용 그릇 안에서 김치는 주방가위로 잘게 자르고, 스팸은 숟가락으로 한입 크기로 나눠 주세요. 캔 가장자리는 날카로우니 손을 대지 마세요.", "일 단계, 재료 손질. 김치는 가위로 잘게 자르고 스팸은 한입 크기로 나눠 주세요."),
            Step("밥 데우기", 3, "밥에 물 1큰술과 식용유를 넣고 고루 풀어 주세요. 접시를 살짝 덮고 틈을 남긴 뒤 {heating_time} 가열해 주세요.", "이 단계, 밥 데우기. 물과 식용유를 넣고 고루 푼 뒤 접시를 살짝 덮고 가열해 주세요.", 3, 2),
            Step("계란 익히기", 2, "계란을 깨서 밥과 충분히 섞어 주세요. 접시를 살짝 덮고 {heating_time} 가열한 뒤 저어 주세요. 액체 계란이 남으면 20초씩 더 가열해 완전히 익혀 주세요.", "삼 단계, 계란 익히기. 계란을 섞어 가열한 뒤 저어 주세요.", 2, 1),
            Step("김치와 스팸 익히기", 3, "김치와 스팸을 넣어 섞고 접시를 살짝 덮어 {heating_time} 가열해 주세요. 중간에 한 번 저어 주세요.", "사 단계, 김치와 스팸 익히기. 김치와 스팸을 넣고 가열한 뒤 중간에 한 번 저어 주세요.", 3, 2),
            Step("마무리", 1, "참기름을 넣고 잘 섞어 주세요. 김치와 스팸이 뜨거워졌는지 확인하고, 차가운 부분이 있으면 20초씩 추가 가열해 주세요.", "오 단계, 마무리. 참기름을 넣고 잘 섞으면 완성이에요."),
        ),
        sources=("세이브밀 조건 A 전자레인지 조리 안내",),
        variant="A",
    ),
    Recipe(
        folder="비빔국수",
        title="비빔국수",
        total_minutes=15,
        ingredients=("소면 1인분", "신김치 ½컵", "고추장 1½숟가락", "설탕 ½숟가락", "식초 ½숟가락", "참기름 ½숟가락", "물 500ml"),
        ingredient_tags=("김치", "소면"),
        steps=(
            Step("김치와 양념 준비", 2, "전자레인지용 큰 그릇 안에서 김치를 주방가위로 잘게 잘라 주세요. 고추장, 설탕, 식초, 참기름을 넣고 섞어 둡니다.", "일 단계, 김치와 양념 준비. 김치를 잘게 자르고 양념을 섞어 주세요."),
            Step("면과 물 담기", 1, "소면을 그릇에 넣고 면이 잠기도록 물 500ml를 부어 주세요. 그릇은 절반 이상 비워 끓어 넘치지 않게 하고, 밀폐하지 말고 접시를 비스듬히 덮어 주세요.", "이 단계, 면과 물 담기. 소면과 물을 넣고 접시를 비스듬히 덮어 주세요."),
            Step("면 익히기", 7, "그릇이 뜨거우니 조심해 전자레인지에 넣고 {heating_time} 가열해 주세요. 끓어 넘치면 바로 멈추세요. 시간이 끝난 뒤 1분 두고 면이 익었는지 확인하고, 덜 익었으면 20초씩 추가해 주세요.", "삼 단계, 면 익히기. 전자레인지에 넣고 가열해 주세요.", 7, 5),
            Step("면 헹구기", 3, "오븐 장갑이나 마른 행주로 그릇을 꺼내세요. 접시를 비스듬히 대고 뜨거운 물을 조금씩 따라 버린 다음, 찬물을 받아 면을 헹구고 다시 조심히 따라 버립니다. 뜨거운 김과 물을 주의하세요.", "사 단계, 면 헹구기. 뜨거운 물을 조심히 따라 버리고 찬물로 헹궈 주세요."),
            Step("비비기", 2, "양념장에 물기를 뺀 면과 김치를 넣고 고루 비벼 주세요. 양념이 뭉치면 물을 1숟가락씩 더해 풀어 주세요.", "오 단계, 비비기. 양념장에 면과 김치를 넣고 고루 비비면 완성이에요."),
        ),
        sources=("세이브밀 조건 A 전자레인지 조리 안내",),
        variant="A",
    ),
    Recipe(
        folder="참치마요덮밥",
        title="참치마요덮밥",
        total_minutes=8,
        ingredients=("밥 1공기", "참치캔 1개", "마요네즈 2숟가락", "김가루 2숟가락"),
        ingredient_tags=("밥", "참치"),
        steps=(
            Step("참치 기름 빼기", 1, "캔 가장자리를 조심해 참치캔을 열고, 숟가락으로 참치를 눌러 기름을 따라 버려 주세요. 캔 뚜껑은 바로 치워 주세요.", "일 단계, 참치 기름 빼기. 참치캔 기름을 눌러 따라 버려 주세요."),
            Step("밥 데우기", 2, "밥에 물 1큰술을 뿌리고 접시를 살짝 덮어 {heating_time} 가열해 주세요. 밥이 고루 뜨거워지도록 중간에 한 번 저어 주세요.", "이 단계, 밥 데우기. 물을 뿌리고 접시를 살짝 덮어 가열해 주세요.", 2, 1),
            Step("참치마요 만들기", 2, "참치와 마요네즈를 그릇에 넣고 숟가락으로 고루 섞어 주세요.", "삼 단계, 참치마요 만들기. 참치와 마요네즈를 고루 섞어 주세요."),
            Step("밥에 올리기", 1, "따뜻한 밥을 그릇에 고르게 펴 주세요.", "사 단계, 밥에 올리기. 따뜻한 밥을 그릇에 고르게 펴 주세요."),
            Step("마무리", 1, "밥 위에 참치마요와 김가루를 올려 주세요. 참치가 차가우면 20초씩 짧게 더 데워 주세요.", "오 단계, 마무리. 참치마요와 김가루를 올리면 완성이에요."),
        ),
        sources=("세이브밀 조건 A 전자레인지 조리 안내",),
        variant="A",
    ),
)

THEME_PALETTES: dict[str, dict[str, str]] = {
    "Default": {
        "background": "#F4F5F7",
        "surface": "#FFFFFF",
        "text": "#1F2937",
        "muted": "#4B5563",
        "accent": "#475569",
        "accent_hover": "#334155",
        "button_text": "#FFFFFF",
        "soft": "#E5E7EB",
        "complete": "#CBD5E1",
        "border": "#D1D5DB",
        "scheme": "light",
    },
    "Black": {
        "background": "#09090B",
        "surface": "#18181B",
        "text": "#FFFFFF",
        "muted": "#E4E4E7",
        "accent": "#FBBF24",
        "accent_hover": "#F59E0B",
        "button_text": "#18181B",
        "soft": "#27272A",
        "complete": "#3F3F46",
        "border": "#52525B",
        "scheme": "dark",
    },
    "Cream": {
        "background": "#FFF7ED",
        "surface": "#FFFBEB",
        "text": "#292524",
        "muted": "#57534E",
        "accent": "#C2410C",
        "accent_hover": "#9A3412",
        "button_text": "#FFFFFF",
        "soft": "#FED7AA",
        "complete": "#FDBA74",
        "border": "#E7D5C2",
        "scheme": "light",
    },
    "Ocean": {
        "background": "#EFF6FF",
        "surface": "#FFFFFF",
        "text": "#0F172A",
        "muted": "#334155",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "button_text": "#FFFFFF",
        "soft": "#DBEAFE",
        "complete": "#BFDBFE",
        "border": "#BFDBFE",
        "scheme": "light",
    },
}


def theme_checkbox_key(name: str) -> str:
    return f"theme-choice-{name.lower()}"


def select_theme(name: str) -> None:
    selected = name if st.session_state[theme_checkbox_key(name)] else "Default"
    st.session_state.theme = selected
    for theme_name in THEME_PALETTES:
        st.session_state[theme_checkbox_key(theme_name)] = theme_name == selected


def select_kitchen_profile() -> None:
    st.session_state.kitchen_profile = st.session_state.kitchen_profile_selector
    reset_step_timer()


def select_microwave_wattage() -> None:
    st.session_state.microwave_wattage = st.session_state.microwave_wattage_selector
    reset_step_timer()


def reset_step_timer() -> None:
    st.session_state.step_timer_started_at = time.monotonic()


def sync_auto_advance_timer(timer_key: str) -> None:
    if not st.session_state.auto_advance:
        st.session_state.step_timer_key = None
        st.session_state.step_timer_started_at = None
        return
    if (
        st.session_state.get("step_timer_key") != timer_key
        or st.session_state.get("step_timer_started_at") is None
    ):
        st.session_state.step_timer_key = timer_key
        st.session_state.step_timer_started_at = time.monotonic()


@st.cache_data(show_spinner=False)
def read_asset(path: str) -> bytes | None:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return None
    return file_path.read_bytes()


@st.cache_data(show_spinner=False)
def step_image_canvas(path: str) -> Image.Image | None:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return None
    try:
        with Image.open(file_path) as source:
            image = source.convert("RGB")
            canvas_width = (image.height * 3 + 1) // 2
            canvas = Image.new("RGB", (canvas_width, image.height), "white")
            canvas.paste(image, ((canvas_width - image.width) // 2, 0))
            return canvas
    except Exception:
        return None


def show_image_safe(image_obj: Any, caption: str | None = None, missing_text: str = "이미지를 찾을 수 없습니다.") -> None:
    if image_obj is None:
        st.caption(missing_text)
        return
    if isinstance(image_obj, (str, Path)):
        p = Path(image_obj)
        if not p.exists() or not p.is_file():
            st.caption(f"{missing_text} ({p.name})")
            return
        st.image(str(p), caption=caption, width="stretch")
        return
    st.image(image_obj, caption=caption, width="stretch")


def _resolve_folder(base_dir: Path, folder_name: str) -> Path:
    direct = base_dir / folder_name
    if direct.exists() and direct.is_dir():
        return direct
    for form in ("NFC", "NFD"):
        candidate = base_dir / unicodedata.normalize(form, folder_name)
        if candidate.exists() and candidate.is_dir():
            return candidate
    if base_dir.exists() and base_dir.is_dir():
        target_nfc = unicodedata.normalize("NFC", folder_name)
        target_nfd = unicodedata.normalize("NFD", folder_name)
        for entry in base_dir.iterdir():
            if entry.is_dir():
                en_nfc = unicodedata.normalize("NFC", entry.name)
                en_nfd = unicodedata.normalize("NFD", entry.name)
                if target_nfc in (en_nfc, en_nfd) or target_nfd in (en_nfc, en_nfd):
                    return entry
    return direct


def _find_file_flexible(
    folder: Path,
    stem_candidates: list[str],
    extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp"),
) -> Path | None:
    if not folder.exists() or not folder.is_dir():
        return None

    normalized_stems = set()
    for s in stem_candidates:
        normalized_stems.add(unicodedata.normalize("NFC", s))
        normalized_stems.add(unicodedata.normalize("NFD", s))

    allowed_exts = {e.lower() for e in extensions}

    for ext in extensions:
        for stem in stem_candidates:
            for form in ("NFC", "NFD"):
                p = folder / f"{unicodedata.normalize(form, stem)}{ext}"
                if p.exists() and p.is_file():
                    return p

    for entry in folder.iterdir():
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in allowed_exts:
            continue
        entry_stem_nfc = unicodedata.normalize("NFC", entry.stem)
        entry_stem_nfd = unicodedata.normalize("NFD", entry.stem)
        if entry_stem_nfc in normalized_stems or entry_stem_nfd in normalized_stems:
            return entry

    return None


def asset_path(recipe: Recipe, kind: str, step: int | None = None) -> Path:
    base_folder = _resolve_folder(APP_DIR, recipe.folder)
    if step is None and kind in {"image", "voice"}:
        raise ValueError(f"A step number is required for {kind} assets.")

    if kind == "voice":
        candidates = [
            _resolve_folder(base_folder, "A안_전자레인지") if recipe.variant == "A" else base_folder,
            base_folder,
        ]
        stems = (
            [f"{recipe.folder}_A_{step}단계_voice", f"{recipe.folder}_{step}단계_voice"]
            if recipe.variant == "A"
            else [f"{recipe.folder}_{step}단계_voice"]
        )
        for folder in candidates:
            found_audio = _find_file_flexible(folder, stems, extensions=(".mp3", ".wav", ".m4a"))
            if found_audio:
                return found_audio
        return candidates[0] / f"{stems[0]}.mp3"

    folder = _resolve_folder(base_folder, "A안_전자레인지") if recipe.variant == "A" else base_folder
    prefix = f"{recipe.folder}_A_" if recipe.variant == "A" else f"{recipe.folder}_"

    if kind == "finished":
        stems = [f"{prefix}0_완성이미지", f"{recipe.folder}_0_완성이미지"]
    elif kind == "infographic":
        stems = [f"{prefix}0_인포그래픽", f"{recipe.folder}_0_인포그래픽"]
    elif kind == "image":
        stems = [f"{prefix}{step}단계_이미지", f"{recipe.folder}_{step}단계_이미지"]
    else:
        raise ValueError(f"Unsupported asset kind: {kind}")

    found = _find_file_flexible(folder, stems)
    return found if found else folder / f"{stems[0]}.png"


def recipes_for_profile() -> tuple[Recipe, ...]:
    return MICROWAVE_RECIPES if st.session_state.kitchen_profile == "A" else RECIPES


def selected_microwave_minutes(step: Step) -> int | None:
    if st.session_state.microwave_wattage == "700W":
        return step.microwave_minutes_700w
    if st.session_state.microwave_wattage == "1000W":
        return step.microwave_minutes_1000w
    return None


def step_duration_seconds(recipe: Recipe, step: Step) -> int:
    if recipe.variant == "A" and step.microwave_minutes_700w is not None:
        minutes = selected_microwave_minutes(step)
        if minutes is not None:
            return max(1, minutes * 60)
    return max(1, step.minutes * 60)


def cooking_instruction(step: Step) -> str:
    if step.microwave_minutes_700w is None:
        return step.instruction
    minutes = selected_microwave_minutes(step)
    heating_time = f"약 {minutes}분" if minutes is not None else "1분부터 짧게"
    return step.instruction.replace("{heating_time}", heating_time)


def go_to(phase: str) -> None:
    st.session_state.phase = phase


def render_home() -> None:
    st.markdown('<div class="eyebrow">맞춤 레시피 추천</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">세이브밀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">집에 있는 재료로 만드는 쉬운 한 끼</p>', unsafe_allow_html=True)

    st.subheader("주방 환경을 선택해 주세요")
    st.radio(
        "조리 환경",
        options=("A", "B"),
        format_func=lambda value: (
            "자취생 초간단 열원 · 전자레인지 중심"
            if value == "A"
            else "일반 가정 · 가스레인지/인덕션 다구 열원"
        ),
        horizontal=False,
        key="kitchen_profile_selector",
        on_change=select_kitchen_profile,
        label_visibility="collapsed",
    )

    if st.session_state.kitchen_profile == "A":
        st.selectbox(
            "전자레인지 출력",
            options=("700W", "1000W", "모름"),
            key="microwave_wattage_selector",
            on_change=select_microwave_wattage,
            help="출력을 모르면 기기 뒷면이나 문 안쪽의 표시를 확인해 주세요. 모를 때는 1분부터 짧게 가열하고 20초씩 추가하며 상태를 확인합니다.",
        )
        st.caption("칼·도마·가스레인지 없이 주방가위와 전자레인지용 그릇으로 만드는 메뉴를 추천해요.")
    else:
        st.info("칼·도마·냄비·프라이팬을 사용하는 단계별 화력 조절 레시피를 보여드려요.")

    recipes_for_kitchen = recipes_for_profile()
    all_tags = sorted({tag for recipe in recipes_for_kitchen for tag in recipe.ingredient_tags})
    selected_tags = st.multiselect(
        "가지고 있는 재료를 선택해 주세요",
        all_tags,
        placeholder="예: 밥, 계란, 김치",
    )
    st.caption("재료가 많이 맞는 메뉴부터 추천해요. 재료를 고르지 않으면 전체 메뉴를 보여드려요.")

    recipes = sorted(
        recipes_for_kitchen,
        key=lambda item: (-len(set(selected_tags) & set(item.ingredient_tags)), item.title),
    )

    columns = st.columns(2)
    for index, recipe in enumerate(recipes):
        matching = len(set(selected_tags) & set(recipe.ingredient_tags))
        with columns[index % 2]:
            show_image_safe(asset_path(recipe, "finished"), missing_text="완성 이미지 준비 중")
            st.markdown(f"### {recipe.title}")
            st.caption(f"1인분 · 약 {recipe.total_minutes}분")
            if selected_tags:
                st.caption(f"선택 재료 {matching}개 포함")
            if st.button("메뉴 자세히 보기", key=f"open-{recipe.folder}", width="stretch"):
                st.session_state.recipe_folder = recipe.folder
                st.session_state.phase = "detail"
                st.rerun()


def render_detail(recipe: Recipe) -> None:
    if st.button("← 메뉴 목록", key="back-home"):
        go_to("home")
        st.rerun()

    st.markdown(f'<h1 class="main-title">{recipe.title}</h1>', unsafe_allow_html=True)
    st.caption(f"1인분 · 총 소요 시간 약 {recipe.total_minutes}분")
    show_image_safe(asset_path(recipe, "finished"), missing_text="완성 이미지 준비 중")

    st.subheader("오늘의 재료")
    st.markdown("\n".join(f"- {ingredient}" for ingredient in recipe.ingredients))

    if recipe.variant == "A":
        with st.expander("도구 대체 팁 · 전자레인지 도움말"):
            st.markdown(
                "- 칼과 도마 대신 전자레인지용 그릇 안에서 주방가위로 자르세요.\n"
                "- 전자레인지용 그릇만 사용하고, 금속 장식이 있는 그릇이나 밀폐 뚜껑은 쓰지 마세요.\n"
                "- 접시는 틈을 남겨 덮고, 뜨거운 그릇은 마른 행주나 오븐 장갑으로 잡으세요.\n"
                "- 출력이 불확실하면 1분부터 짧게 돌리고, 상태를 확인하며 20초씩 추가하세요."
            )
    else:
        with st.expander("도구와 화력 도움말"):
            st.markdown(
                "- 강불: 물을 빠르게 끓이거나 팬을 달굴 때 사용해요.\n"
                "- 중불: 재료를 고르게 익히고 볶을 때 사용해요.\n"
                "- 약불: 양념이 타지 않게 천천히 익히거나 마무리할 때 사용해요."
            )

    savings = calculate_savings(recipe.title)
    if savings is not None:
        st.subheader("오늘의 절감액")
        cost_columns = st.columns(3)
        cost_columns[0].metric("1인분 재료비", f"{savings['ingredient_cost']:,}원")
        cost_columns[1].metric("배달 총액", f"{savings['delivery_total']:,}원")
        cost_columns[2].metric("절감액", f"{savings['savings']:,}원")
        st.caption(f"배달 음식값 {savings['delivery_price']:,}원 + 배달비 {savings['delivery_fee']:,}원")

    st.subheader("요리 순서 한눈에 보기")
    show_image_safe(asset_path(recipe, "infographic"), missing_text="인포그래픽 준비 중")

    with st.expander("참고 레시피 출처"):
        for source in recipe.sources:
            st.markdown(f"- {source}")

    if st.button("요리 시작하기", type="primary", width="stretch"):
        st.session_state.step_index = 0
        st.session_state.phase = "cook"
        st.session_state.auto_advance = False
        st.session_state.step_timer_key = None
        st.session_state.step_timer_started_at = None
        st.rerun()


def advance_step(recipe: Recipe, step_index: int) -> None:
    if step_index + 1 >= len(recipe.steps):
        st.session_state.phase = "done"
        st.session_state.step_timer_key = None
        st.session_state.step_timer_started_at = None
        return
    st.session_state.step_index = step_index + 1
    reset_step_timer()


def format_step_time_label(recipe: Recipe, step: Step) -> str:
    if recipe.variant == "A" and step.microwave_minutes_700w is not None:
        minutes = selected_microwave_minutes(step)
        if minutes is not None:
            return f"예상 약 {step.minutes}분 · 전자레인지 {st.session_state.microwave_wattage} 약 {minutes}분"
        return f"예상 약 {step.minutes}분 · 출력 모름(1분부터 확인)"
    return f"예상 약 {step.minutes}분"


def format_countdown(seconds: int) -> str:
    clamped = max(0, seconds)
    mins, secs = divmod(clamped, 60)
    return f"{mins:02d}:{secs:02d}"


def render_cooking(recipe: Recipe) -> None:
    step_index = min(max(st.session_state.step_index, 0), len(recipe.steps) - 1)
    st.session_state.step_index = step_index
    step = recipe.steps[step_index]

    timer_key = f"{recipe.folder}-{recipe.variant}-{step_index}"
    sync_auto_advance_timer(timer_key)

    st.markdown(f'<h1 class="main-title">{recipe.title}</h1>', unsafe_allow_html=True)
    st.caption(f"STEP {step_index + 1} / {len(recipe.steps)} · 단계 번호를 눌러 이동할 수 있어요")

    progress_columns = st.columns(len(recipe.steps))
    for index, column in enumerate(progress_columns):
        state = "complete" if index < step_index else "current" if index == step_index else "upcoming"
        marker_prefix = "✓ " if state == "complete" else ""
        with column:
            if st.button(
                f"{marker_prefix}{index + 1}",
                key=f"step-jump-{recipe.folder}-{recipe.variant}-{index}",
                width="stretch",
                type="primary" if state == "current" else "secondary",
            ):
                st.session_state.step_index = index
                reset_step_timer()
                st.rerun()

    badge, setting = st.columns([1.4, 1])
    with badge:
        st.markdown(f'<div class="time-badge">⏱ {format_step_time_label(recipe, step)}</div>', unsafe_allow_html=True)

    with setting:
        st.checkbox(
            "자동 다음 단계 (예상 시간)",
            key="auto_advance",
            on_change=reset_step_timer,
            help="단계별 예상 시간 기준으로 자동 전환합니다.",
        )

    remaining_seconds: int | None = None
    if st.session_state.auto_advance and st.session_state.get("step_timer_started_at") is not None:
        duration = step_duration_seconds(recipe, step)
        elapsed = time.monotonic() - float(st.session_state.step_timer_started_at)
        remaining_seconds = max(0, int(duration - elapsed + 0.999))
        st.info(f"자동 전환 타이머 작동 중 · 남은 시간 {format_countdown(remaining_seconds)}")

    st.subheader(step.title)
    show_image_safe(
        step_image_canvas(str(asset_path(recipe, "image", step_index + 1))),
        missing_text="단계 이미지 준비 중",
    )
    st.info(cooking_instruction(step))

    audio_path = asset_path(recipe, "voice", step_index + 1)
    audio_bytes = read_asset(str(audio_path))
    if audio_bytes:
        mime_type = (
            "audio/wav"
            if audio_path.suffix.lower() == ".wav"
            else "audio/mp4"
            if audio_path.suffix.lower() == ".m4a"
            else "audio/mp3"
        )
        st.audio(audio_bytes, format=mime_type)
    else:
        st.caption(f"음성 안내 파일이 없습니다. ({audio_path.name})")

    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("이전 단계", key=f"prev-{recipe.folder}-{step_index}", disabled=step_index == 0, width="stretch"):
            st.session_state.step_index = step_index - 1
            reset_step_timer()
            st.rerun()
    with col_next:
        next_label = "요리 완료" if step_index + 1 >= len(recipe.steps) else "다음 단계"
        if st.button(next_label, key=f"next-{recipe.folder}-{step_index}", type="primary", width="stretch"):
            advance_step(recipe, step_index)
            st.rerun()

    if st.button("요리 안내 종료", key="exit-cook"):
        st.session_state.step_timer_key = None
        st.session_state.step_timer_started_at = None
        st.session_state.phase = "detail"
        st.rerun()

    if st.session_state.auto_advance and remaining_seconds is not None:
        if remaining_seconds <= 0:
            advance_step(recipe, step_index)
            st.rerun()
        time.sleep(1)
        st.rerun()


def render_done(recipe: Recipe) -> None:
    st.markdown('<div class="eyebrow">오늘의 요리 완료</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="main-title">{recipe.title} 완성!</h1>', unsafe_allow_html=True)
    show_image_safe(asset_path(recipe, "finished"), missing_text="완성 이미지 준비 중")
    st.success("수고하셨어요. 맛있게 드세요!")

    if st.button("다른 메뉴 고르기", type="primary", width="stretch"):
        st.session_state.phase = "home"
        st.rerun()
    if st.button("이 메뉴 다시 요리하기", width="stretch"):
        st.session_state.step_index = 0
        st.session_state.phase = "cook"
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="세이브밀",
        page_icon="🍳",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    st.session_state.setdefault("phase", "home")
    st.session_state.setdefault("recipe_folder", RECIPES[0].folder)
    st.session_state.setdefault("step_index", 0)
    st.session_state.setdefault("auto_advance", False)
    st.session_state.setdefault("step_timer_key", None)
    st.session_state.setdefault("step_timer_started_at", None)
    st.session_state.setdefault("kitchen_profile", "B")
    st.session_state.setdefault("microwave_wattage", "700W")
    st.session_state.setdefault("kitchen_profile_selector", st.session_state.kitchen_profile)
    st.session_state.setdefault("microwave_wattage_selector", st.session_state.microwave_wattage)
    st.session_state.setdefault("theme", "Default")

    if st.session_state.theme not in THEME_PALETTES:
        st.session_state.theme = "Default"

    for theme_name in THEME_PALETTES:
        st.session_state.setdefault(theme_checkbox_key(theme_name), theme_name == st.session_state.theme)

    _, theme_column = st.columns([12, 1])
    with theme_column:
        with st.popover("Theme"):
            for theme_name in THEME_PALETTES:
                st.checkbox(
                    theme_name,
                    key=theme_checkbox_key(theme_name),
                    on_change=select_theme,
                    args=(theme_name,),
                )

    palette = THEME_PALETTES[st.session_state.theme]
    theme_css = f"""
    :root {{ color-scheme: {palette["scheme"]}; }}
    .stApp, .stApp [data-testid="stAppViewContainer"], .stApp [data-testid="stMain"] {{
        background: {palette["background"]} !important;
        color: {palette["text"]} !important;
    }}
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: {palette["text"]} !important;
    }}
    .stApp [data-testid="stCaptionContainer"] p {{ color: {palette["muted"]} !important; }}
    .main-title, .eyebrow, a {{ color: {palette["accent"]} !important; }}
    .sub-title {{ color: {palette["muted"]}; }}
    .time-badge {{ background: {palette["soft"]}; color: {palette["text"]} !important; }}
    .stAlert {{
        background: {palette["surface"]} !important;
        color: {palette["text"]} !important;
        border-color: {palette["border"]} !important;
    }}
    [data-testid="stPopoverBody"] {{
        width: 190px !important;
        min-width: 190px !important;
        max-width: 190px !important;
        background: {palette["surface"]} !important;
        color: {palette["text"]} !important;
        border: 1px solid {palette["border"]};
        padding: .35rem !important;
    }}
    [data-testid="stPopoverBody"] > div {{ background: {palette["surface"]} !important; }}
    [data-testid="stPopoverBody"] * {{ color: {palette["text"]} !important; }}
    [data-baseweb="select"] > div {{
        background: {palette["surface"]} !important;
        color: {palette["text"]} !important;
    }}
    [data-baseweb="select"] * {{ color: {palette["text"]} !important; }}
    [data-baseweb="select"] input::placeholder {{ color: {palette["muted"]} !important; }}
    [data-baseweb="menu"] {{ background: {palette["surface"]}; }}
    [data-baseweb="menu"] * {{ color: {palette["text"]} !important; }}
    div.stButton > button[kind="primary"] {{
        background: {palette["accent"]};
        color: {palette["button_text"]};
        border-color: {palette["border"]};
    }}
    div.stButton > button[kind="primary"]:hover {{
        background: {palette["accent_hover"]};
        color: {palette["button_text"]};
        border-color: {palette["accent_hover"]};
    }}
    div.stButton > button[kind="secondary"] {{
        background: {palette["soft"]};
        color: {palette["text"]};
        border-color: {palette["border"]};
    }}
    div[data-testid="stPopover"] {{ width: fit-content; margin-left: auto; }}
    div[data-testid="stPopover"] > div > button {{
        min-height: 2rem;
        padding: .25rem .7rem;
        background: {palette["surface"]};
        color: {palette["text"]};
        border: 1px solid {palette["border"]};
    }}
    """

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewBlockContainer"] {{
            max-width: 640px !important;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        .main-title {{ font-size: 2rem; font-weight: 800; margin: 0; }}
        .sub-title {{ margin: .25rem 0 1.2rem; }}
        .eyebrow {{ font-size: .85rem; font-weight: 700; }}
        .time-badge {{ display: inline-block; border-radius: 999px; padding: .45rem .8rem; font-weight: 700; }}
        div.stButton > button {{ border-radius: 12px; min-height: 2.5rem; font-weight: 700; }}
        div[data-testid="stImage"] img {{ border-radius: 16px; }}
        {theme_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

    available_recipes = recipes_for_profile()
    recipe = next(
        (item for item in available_recipes if item.folder == st.session_state.recipe_folder),
        available_recipes[0],
    )

    phase = st.session_state.phase
    if phase == "home":
        render_home()
    elif phase == "detail":
        render_detail(recipe)
    elif phase == "cook":
        render_cooking(recipe)
    elif phase == "done":
        render_done(recipe)
    else:
        st.session_state.phase = "home"
        st.rerun()


if __name__ == "__main__":
    main()
