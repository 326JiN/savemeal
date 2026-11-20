from __future__ import annotations

import base64
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import unicodedata
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image


APP_DIR = Path(__file__).resolve().parent
CONTROLS_COMPONENT = components.declare_component(
    "savemeal_cooking_controls",
    path=str(APP_DIR / "components" / "cooking_controls"),
)


@dataclass(frozen=True)
class Step:
    title: str
    minutes: int
    instruction: str
    voice: str


@dataclass(frozen=True)
class Recipe:
    folder: str
    title: str
    total_minutes: int
    ingredients: tuple[str, ...]
    ingredient_tags: tuple[str, ...]
    steps: tuple[Step, ...]
    sources: tuple[str, ...]


DELIVERY_FEE = 3_000

# 원본 절감액 계산 표의 구매단위 단가(원)입니다.
UNIT_PRICES = {
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

RECIPE_COST_USAGE = {
    "김치스팸볶음밥": {"밥": (200, "g"), "신김치": (100, "g"), "스팸": (67, "g"), "계란": (1, "개"), "식용유": (30, "ml"), "참기름": (7.5, "ml")},
    "김치찌개": {"신김치": (100, "g"), "돼지고기": (100, "g"), "두부": (150, "g"), "대파": (25, "g"), "고춧가루": (7, "g"), "다진마늘": (7, "g"), "간장": (15, "ml"), "식용유": (15, "ml"), "물": (360, "ml")},
    "참치마요덮밥": {"밥": (200, "g"), "참치캔": (100, "g"), "마요네즈": (30, "g"), "계란": (2, "개"), "식용유": (7.5, "ml")},
    "제육볶음덮밥": {"밥": (200, "g"), "돼지고기": (150, "g"), "양파": (50, "g"), "대파": (25, "g"), "식용유": (15, "ml"), "고추장": (30, "g"), "간장": (15, "ml"), "설탕": (12, "g"), "다진마늘": (7, "g")},
    "비빔국수": {"소면": (100, "g"), "신김치": (50, "g"), "고추장": (30, "g"), "설탕": (6, "g"), "식초": (7.5, "ml"), "참기름": (7.5, "ml"), "물": (720, "ml")},
}

DELIVERY_PRICES = {
    "김치스팸볶음밥": 5200,
    "김치찌개": 6000,
    "참치마요덮밥": 3800,
    "제육볶음덮밥": 6500,
    "비빔국수": 6900,
}


def calculate_savings(menu_name: str) -> dict[str, int]:
    cost = sum(
        (
            Decimal(str(usage))
            * Decimal(str(UNIT_PRICES.get(ingredient, 0)))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        for ingredient, (usage, _unit) in RECIPE_COST_USAGE[menu_name].items()
    )
    ingredient_cost = int(cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    delivery_price = DELIVERY_PRICES[menu_name]
    delivery_total = delivery_price + DELIVERY_FEE
    return {
        "ingredient_cost": ingredient_cost,
        "delivery_price": delivery_price,
        "delivery_fee": DELIVERY_FEE,
        "delivery_total": delivery_total,
        "savings": delivery_total - ingredient_cost,
    }


RECIPES = (
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
            Step("재료 썰기", 3, "김치 종이컵 1컵은 가위로 1cm 폭으로 자르고, 스팸 종이컵 ½컵은 새끼손톱 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요.", "일 단계, 재료 썰기. 김치는 가위로 일 센티미터 폭으로 자르고 스팸은 새끼손톱 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요."),
            Step("계란 부치기", 2, "중불에 식용유 1숟가락을 두르고 계란 1개를 흰자가 익을 때까지 부쳐 접시에 옮겨 주세요. 기름이 튀니 얼굴을 팬에서 떼세요.", "이 단계, 계란 부치기. 중불에 식용유 한 숟가락을 두르고 계란을 흰자가 하얗게 굳을 때까지 부쳐 접시에 옮겨 주세요. 기름이 튀니 얼굴을 떼세요."),
            Step("스팸 볶기", 2, "중불에 식용유 1숟가락을 두르고 스팸을 겉이 노릇해질 때까지 볶아 주세요.", "삼 단계, 스팸 볶기. 같은 팬에 식용유 한 숟가락을 두르고 스팸을 겉이 노릇해질 때까지 볶아 주세요."),
            Step("김치 볶기", 2, "중불에서 김치를 넣고 숨이 죽을 때까지 볶아 주세요. 많이 시면 설탕 ½숟가락을 넣으세요.", "사 단계, 김치 볶기. 중불 그대로 김치를 넣고 숨이 죽을 때까지 볶아 주세요. 김치가 많이 시면 설탕 반 숟가락을 넣으세요."),
            Step("밥 볶기", 3, "약불로 줄이고 찬밥 종이컵 1컵 반을 넣어 덩어리를 풀며 볶아 주세요. 불을 끄고 참기름 ½숟가락을 두른 뒤 계란을 올리세요.", "오 단계, 밥 볶기. 약불로 줄이고 찬밥을 넣어 덩어리를 풀며 볶아 주세요. 불을 끄고 참기름 반 숟가락을 두른 뒤 계란을 올리면 완성이에요."),
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
            Step("재료 썰기", 3, "김치 종이컵 1컵은 가위로 2cm 폭으로 자르고 목살 종이컵 1컵은 한입 크기로 썰어 주세요. 대파 ¼대와 선택한 두부도 썰고 칼날 반대쪽에 손가락을 두세요.", "일 단계, 재료 썰기. 김치는 가위로 이 센티미터 폭으로 자르고 목살은 한입 크기, 대파는 어슷하게 썰어 주세요. 칼날 반대쪽에 손가락을 두세요."),
            Step("고기·김치 볶기", 4, "중불에 식용유 1숟가락을 두르고 목살을 볶은 뒤 김치를 넣어 숨이 죽을 때까지 볶아 주세요. 많이 시면 설탕 ½숟가락을 넣으세요.", "이 단계, 고기와 김치 볶기. 중불에 식용유 한 숟가락을 두르고 목살을 겉면 색이 변할 때까지 볶은 뒤 김치를 넣어 숨이 죽을 때까지 볶아 주세요. 김치가 많이 시면 설탕 반 숟가락을 넣으세요."),
            Step("물 붓고 끓이기", 5, "물 종이컵 2컵을 붓고 강불에서 끓어오를 때까지 기다려 주세요. 끓는 국물이 튀니 얼굴을 냄비에서 떼세요.", "삼 단계, 물 붓고 끓이기. 물 두 컵을 붓고 강불에서 끓어오를 때까지 기다려 주세요. 국물이 튀니 얼굴을 떼세요."),
            Step("양념 넣기", 7, "중불로 줄이고 고춧가루 1숟가락, 다진마늘 ½숟가락, 국간장 1숟가락을 넣어 끓여 주세요.", "사 단계, 양념 넣기. 중불로 줄이고 고춧가루 한 숟가락, 다진마늘 반 숟가락, 국간장 한 숟가락을 넣어 칠 분 정도 끓여 주세요."),
            Step("대파 넣고 마무리", 3, "선택한 두부와 대파를 넣고 약불에서 3분 더 끓인 뒤 불을 꺼 주세요.", "오 단계, 대파 넣고 마무리. 두부와 대파를 넣고 약불에서 삼 분 정도 더 끓인 뒤 불을 끄면 완성이에요."),
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
            Step("김치 썰기", 1, "김치 종이컵 ½컵을 가위로 잘게 잘라 주세요.", "일 단계, 김치 썰기. 김치를 가위로 잘게 잘라 주세요."),
            Step("양념장 만들기", 2, "고추장 1½숟가락, 설탕 ½숟가락, 식초 ½숟가락, 참기름 ½숟가락을 먼저 섞어 주세요.", "이 단계, 양념장 만들기. 고추장 한 숟가락 반, 설탕과 식초, 참기름을 반 숟가락씩 넣어 먼저 섞어 주세요."),
            Step("면 삶기", 4, "강불에서 소면을 삶고 끓어오를 때마다 찬물 ½컵씩 두 번 부은 뒤 세 번째에 불을 꺼 주세요. 면을 천천히 넣어 뜨거운 물이 튀지 않게 하세요.", "삼 단계, 면 삶기. 끓는 물에 소면을 천천히 넣고, 끓어오를 때마다 찬물 반 컵씩 두 번 부어 주세요. 세 번째로 끓으면 불을 끄세요."),
            Step("면 헹구기", 2, "면을 체에 쏟아 찬물에 비벼 헹군 뒤 물기를 털어 주세요. 뜨거운 김에 데지 않게 얼굴을 떼세요.", "사 단계, 면 헹구기. 면을 체에 쏟아 찬물에 비벼 헹구고 물기를 털어 주세요. 뜨거운 김을 조심하세요."),
            Step("비비기", 1, "양념장에 면과 김치를 넣고 고루 비벼 주세요.", "오 단계, 비비기. 양념장에 면과 김치를 넣고 고루 비비면 완성이에요."),
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
            Step("재료 썰기", 3, "양파 ¼개는 채 썰고 대파 ¼대는 어슷하게 썰어 주세요. 고기는 핏물을 닦아 한입 크기로 썰고 칼날 반대쪽에 손가락을 두세요.", "일 단계, 재료 썰기. 양파는 채 썰고 대파는 어슷하게, 고기는 핏물을 닦아 한입 크기로 썰어 주세요. 칼날 반대쪽에 손가락을 두세요."),
            Step("고기 양념하기", 12, "고추장 1½숟가락, 간장 1숟가락, 설탕 1숟가락, 다진마늘 ½숟가락을 섞어 고기를 버무리고 10분 두세요.", "이 단계, 고기 양념하기. 고추장 한 숟가락 반, 간장 한 숟가락, 설탕 한 숟가락, 다진마늘 반 숟가락을 섞고 고기를 고루 버무려 십 분 정도 두세요."),
            Step("고기 볶기", 5, "중불에 식용유 1숟가락을 두르고 고기를 분홍빛이 사라질 때까지 볶아 주세요. 양념이 타지 않게 계속 뒤적이세요.", "삼 단계, 고기 볶기. 중불에 식용유 한 숟가락을 두르고 고기를 분홍빛이 사라질 때까지 볶아 주세요. 양념이 타지 않게 계속 뒤적이세요."),
            Step("채소 넣고 볶기", 2, "양파를 넣어 숨이 죽을 때까지 볶고 대파를 넣어 섞은 뒤 불을 꺼 주세요.", "사 단계, 채소 넣고 볶기. 양파를 넣어 숨이 죽을 때까지 볶고 대파를 넣어 섞은 뒤 불을 꺼 주세요."),
            Step("밥에 올리기", 1, "그릇에 밥 종이컵 1컵 반을 담고 제육볶음을 올려 주세요.", "오 단계, 밥에 올리기. 그릇에 밥을 담고 제육볶음을 올리면 완성이에요."),
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
            Step("참치 기름 빼기", 1, "참치캔 기름을 숟가락으로 눌러 따라 버려 주세요. 캔 뚜껑 가장자리를 조심하세요.", "일 단계, 참치 기름 빼기. 참치캔 기름을 숟가락으로 눌러 따라 버려 주세요. 캔 뚜껑 가장자리는 날카로우니 조심하세요."),
            Step("참치마요 만들기", 2, "참치와 마요네즈 2숟가락을 고루 섞어 주세요.", "이 단계, 참치마요 만들기. 참치와 마요네즈 두 숟가락을 고루 섞어 주세요."),
            Step("계란 스크램블", 2, "중불에 식용유 ½숟가락을 두르고 계란 2개를 풀어 저으며 익혀 주세요.", "삼 단계, 계란 스크램블. 중불에 식용유 반 숟가락을 두르고 계란 두 개를 풀어 저으며 이 분 정도 몽글몽글 덩어리가 질 때까지 익혀 주세요."),
            Step("밥 담기", 1, "그릇에 밥 종이컵 1컵 반을 담고 스크램블을 올려 주세요.", "사 단계, 밥 담기. 그릇에 밥을 담고 스크램블을 올려 주세요."),
            Step("참치마요 올리기", 1, "스크램블 위에 참치마요를 올리고 김가루 2숟가락을 뿌려 주세요.", "오 단계, 참치마요 올리기. 참치마요를 올리고 김가루를 뿌리면 완성이에요."),
        ),
        sources=(
            "진니찡, 만개의레시피, https://www.10000recipe.com/recipe/6879335",
            "시크제이맘, 만개의레시피, https://www.10000recipe.com/recipe/6867725",
        ),
    ),
)

THEME_PALETTES = {
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


def resolve_existing_path(path: Path) -> Path | None:
    if path.exists():
        return path
    for form in ("NFC", "NFD"):
        candidate = Path(unicodedata.normalize(form, str(path)))
        if candidate.exists():
            return candidate
    return None


@st.cache_data(show_spinner=False)
def read_asset(path: str) -> bytes:
    resolved = resolve_existing_path(Path(path))
    if resolved is None:
        raise FileNotFoundError(f"Asset not found: {path}")
    return resolved.read_bytes()


@st.cache_data(show_spinner=False)
def step_image_canvas(path: str) -> Image.Image:
    resolved = resolve_existing_path(Path(path))
    if resolved is None:
        raise FileNotFoundError(f"Step image not found: {path}")
    with Image.open(resolved) as source:
        image = source.convert("RGB")
    canvas_width = (image.height * 3 + 1) // 2
    canvas = Image.new("RGB", (canvas_width, image.height), "white")
    canvas.paste(image, ((canvas_width - image.width) // 2, 0))
    return canvas


def asset_path(recipe: Recipe, kind: str, step: int | None = None) -> Path:
    folder = resolve_existing_path(APP_DIR / recipe.folder) or (APP_DIR / recipe.folder)
    if kind == "finished":
        target = folder / f"{recipe.folder}_0_완성이미지.png"
    elif kind == "infographic":
        target = folder / f"{recipe.folder}_0_인포그래픽.png"
    else:
        if step is None:
            raise ValueError(f"A step number is required for {kind} assets.")
        suffix = "이미지.png" if kind == "image" else "voice.mp3"
        target = folder / f"{recipe.folder}_{step}단계_{suffix}"
    return resolve_existing_path(target) or target


def render_image_safe(path: Path, caption: str | None = None) -> None:
    resolved = resolve_existing_path(path)
    if resolved is not None:
        st.image(str(resolved), caption=caption, width="stretch")
    else:
        st.warning(f"이미지 파일을 찾을 수 없어요: {path.name}")


def go_to(phase: str) -> None:
    st.session_state.phase = phase


def render_home() -> None:
    st.markdown('<div class="eyebrow">오늘의 한 끼</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">세이브밀</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">집에 있는 재료로 만드는 쉬운 한 끼</p>',
        unsafe_allow_html=True,
    )
    all_tags = sorted({tag for recipe in RECIPES for tag in recipe.ingredient_tags})
    selected_tags = st.multiselect(
        "가지고 있는 재료를 선택해 주세요",
        all_tags,
        placeholder="예: 밥, 계란, 김치",
    )
    st.caption("재료가 많이 맞는 메뉴부터 추천해요. 재료를 고르지 않으면 전체 메뉴를 보여드려요.")

    recipes = sorted(
        RECIPES,
        key=lambda item: (
            -len(set(selected_tags) & set(item.ingredient_tags)),
            item.title,
        ),
    )
    columns = st.columns(2)
    for index, recipe in enumerate(recipes):
        matching = len(set(selected_tags) & set(recipe.ingredient_tags))
        with columns[index % 2]:
            render_image_safe(asset_path(recipe, "finished"))
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
    render_image_safe(asset_path(recipe, "finished"))

    st.subheader("오늘의 재료")
    st.markdown("\n".join(f"- {ingredient}" for ingredient in recipe.ingredients))

    savings = calculate_savings(recipe.title)
    st.subheader("오늘의 절감액")
    cost_columns = st.columns(3)
    cost_columns[0].metric("1인분 재료비", f"{savings['ingredient_cost']:,}원")
    cost_columns[1].metric("배달 총액", f"{savings['delivery_total']:,}원")
    cost_columns[2].metric("절감액", f"{savings['savings']:,}원")
    st.caption(
        f"배달 음식값 {savings['delivery_price']:,}원 + 배달비 {savings['delivery_fee']:,}원"
    )

    st.subheader("요리 순서 한눈에 보기")
    render_image_safe(asset_path(recipe, "infographic"))

    with st.expander("참고 레시피 출처"):
        for source in recipe.sources:
            st.markdown(f"- {source}")

    if st.button("요리 시작하기", type="primary", width="stretch"):
        st.session_state.step_index = 0
        st.session_state.phase = "cook"
        st.session_state.auto_advance = False
        st.rerun()


def advance_step(recipe: Recipe, step_index: int) -> None:
    if step_index + 1 == len(recipe.steps):
        st.session_state.phase = "done"
        return
    st.session_state.step_index = step_index + 1


def render_cooking(recipe: Recipe) -> None:
    step_index = st.session_state.step_index
    step = recipe.steps[step_index]
    st.markdown(f'<h1 class="main-title">{recipe.title}</h1>', unsafe_allow_html=True)
    st.caption(f"STEP {step_index + 1} / {len(recipe.steps)}")

    progress_columns = st.columns(len(recipe.steps))
    for index, column in enumerate(progress_columns):
        state = "complete" if index < step_index else "current" if index == step_index else "upcoming"
        with column:
            st.markdown(
                f'<div class="step-marker {state}">{index + 1}</div>',
                unsafe_allow_html=True,
            )

    badge, setting = st.columns([1, 2])
    with badge:
        st.markdown(
            f'<div class="time-badge">⏱ 예상 약 {step.minutes}분</div>',
            unsafe_allow_html=True,
        )
    with setting:
        st.checkbox(
            "자동 다음 단계 (예상 시간)",
            key="auto_advance",
            help="출처에 없는 예상 조리 시간으로 자동 전환합니다.",
        )

    st.subheader(step.title)
    step_img_path = resolve_existing_path(asset_path(recipe, "image", step_index + 1))
    if step_img_path is not None:
        st.image(step_image_canvas(str(step_img_path)), width="stretch")
    else:
        st.warning(f"단계 이미지 파일을 찾을 수 없어요: {step_index + 1}단계")
    st.info(step.instruction)

    audio_path = resolve_existing_path(asset_path(recipe, "voice", step_index + 1))
    if audio_path is not None:
        audio_bytes = read_asset(str(audio_path))
        audio_base64 = base64.b64encode(audio_bytes).decode("ascii")
    else:
        st.warning(f"음성 파일을 찾을 수 없어요: {step_index + 1}단계")
        audio_base64 = ""

    event: Any = CONTROLS_COMPONENT(
        audio_base64=audio_base64,
        auto_advance=st.session_state.auto_advance,
        cook_seconds=step.minutes * 60,
        step_number=step_index + 1,
        can_go_back=step_index > 0,
        colors=THEME_PALETTES[st.session_state.theme],
        key=f"controls-{recipe.folder}-{step_index + 1}",
        default=None,
    )

    if isinstance(event, dict) and event.get("step_number") == step_index + 1:
        event_id = event.get("event_id")
        if event_id and event_id != st.session_state.get("last_control_event_id"):
            st.session_state.last_control_event_id = event_id
            if event.get("action") == "previous" and step_index > 0:
                st.session_state.step_index = step_index - 1
                st.rerun()
            if event.get("action") == "next":
                advance_step(recipe, step_index)
                st.rerun()

    if st.button("요리 안내 종료", key="exit-cook"):
        st.session_state.phase = "detail"
        st.rerun()


def render_done(recipe: Recipe) -> None:
    st.markdown('<div class="eyebrow">오늘의 요리 완료</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="main-title">{recipe.title} 완성!</h1>', unsafe_allow_html=True)
    render_image_safe(asset_path(recipe, "finished"))
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
    st.session_state.setdefault("theme", "Default")
    if st.session_state.theme not in THEME_PALETTES:
        st.session_state.theme = "Default"
    for theme_name in THEME_PALETTES:
        st.session_state.setdefault(
            theme_checkbox_key(theme_name),
            theme_name == st.session_state.theme,
        )

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
    .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: {palette["text"]} !important;
    }}
    .stApp [data-testid="stCaptionContainer"] p {{ color: {palette["muted"]} !important; }}
    .main-title, .eyebrow, a {{ color: {palette["accent"]} !important; }}
    .sub-title {{ color: {palette["muted"]}; }}
    .time-badge {{ background: {palette["soft"]}; color: {palette["text"]}; }}
    .step-marker {{ background: {palette["soft"]}; color: {palette["text"]}; }}
    .step-marker.current {{ background: {palette["accent"]}; color: {palette["button_text"]}; }}
    .step-marker.complete {{ background: {palette["complete"]}; color: {palette["text"]}; }}
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
    [data-testid="stPopoverBody"] > div {{
        background: {palette["surface"]} !important;
    }}
    [data-testid="stPopoverBody"] * {{ color: {palette["text"]} !important; }}
    [data-baseweb="select"] > div {{
        background: {palette["surface"]} !important;
        color: {palette["text"]} !important;
    }}
    [data-baseweb="select"] * {{ color: {palette["text"]} !important; }}
    [data-baseweb="select"] input::placeholder {{ color: {palette["muted"]} !important; }}
    [data-baseweb="menu"] {{ background: {palette["surface"]}; }}
    [data-baseweb="menu"] * {{ color: {palette["text"]} !important; }}
    div.stButton > button {{
        background: {palette["accent"]};
        color: {palette["button_text"]};
        border-color: {palette["border"]};
    }}
    div.stButton > button:hover {{
        background: {palette["accent_hover"]};
        color: {palette["button_text"]};
        border-color: {palette["accent_hover"]};
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
        .time-badge {{
            display: inline-block; border-radius: 999px;
            padding: .45rem .8rem; font-weight: 700;
        }}
        .step-marker {{
            text-align: center; padding: .5rem; border-radius: 999px;
            font-weight: 700;
        }}
        div.stButton > button {{ border-radius: 12px; min-height: 2.5rem; font-weight: 700; }}
        div[data-testid="stImage"] img {{ border-radius: 16px; }}
        {theme_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

    recipe = next(
        (item for item in RECIPES if item.folder == st.session_state.recipe_folder),
        RECIPES[0],
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
