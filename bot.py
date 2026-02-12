import discord
from discord import app_commands
import json
import os
import time
import random
from collections import Counter
import re

# ---------------- 1. 기본 설정 및 데이터 ----------------
TOKEN = os.getenv("TOKEN")
DATA_FILE = "money.json"
INV_FILE = "inventory.json"

BASE_STATS = {"atk": 3, "def": 1, "hp": 10}

ITEMS = {
    "낡은 목검": {"type": "weapon", "atk": 2, "def": 0, "hp": 0},
    "가죽 갑옷": {"type": "armor", "atk": 0, "def": 5, "hp": 20},
    "금간 철 반지": {"type": "artifact", "atk": 2, "def": 2, "hp": 10}
}

WEAPON_SHOP = {
    "낡은 철검": {"price": 10000, "type": "weapon", "atk": 5, "def": 0, "hp": 0},
    "강철검": {"price": 50000, "type": "weapon", "atk": 15, "def": 0, "hp": 0},
    "강철 플레이트 검": {"price": 300000, "type": "weapon", "atk": 40, "def": 0, "hp": 0},
    "흑요석 단검": {"price": 600000, "type": "weapon", "atk": 80, "def": -5, "hp": 0},
    "판테온의 창과 방패": {"price": 1200000, "type": "weapon", "atk": 80, "def": 15, "hp": 0},
    "용의 발톱": {"price": 6000000, "type": "weapon", "atk": 200, "def": 0, "hp": 0},
    "드래곤 슬레이어의 검": {"price": 10000000, "type": "weapon", "atk": 364, "def": 0, "hp": 0},
    "몰락한 왕의 검": {"price": 32000000, "type": "weapon", "atk": 999, "def": 0, "hp": 0}
    
}

ARMOR_SHOP = {
    "강철 흉갑": {"price": 15000, "type": "armor", "atk": 0, "def": 3, "hp": 20},
    "경비병의 판금 흉갑": {"price": 90000, "type": "armor", "atk": 0, "def": 8, "hp": 50},
    "풀 플레이트": {"price": 400000, "type": "armor", "atk": 0, "def": 20, "hp": 100},
    "흑요석 흉갑": {"price": 900000, "type": "armor", "atk": 0, "def": 5, "hp": 500},
    "미스릴 흉갑": {"price": 3000000, "type": "armor", "atk": 0, "def": 50, "hp": 200},
    "가시 갑옷": {"price": 8000000, "type": "armor", "atk": 20, "def": 70, "hp": 150},
    "워모그의 갑옷": {"price": 20000000, "type": "armor", "atk": 0, "def": 20, "hp": 1500},
}

ARTIFACT_SHOP = {
    "생명의 반지": {"price": 8000, "type": "artifact", "atk": 0, "def": 0, "hp": 30},
    "금 반지": {"price": 300000, "type": "artifact", "atk": 10, "def": 0, "hp": 0},
    "사파이어 목걸이": {"price": 1000000, "type": "artifact", "atk": 3, "def": 10, "hp": 0},
    "루비 수정": {"price": 2000000, "type": "artifact", "atk": 0, "def": 10, "hp": 200},
    "마법이 깃든 엘프의 반지": {"price": 10000000, "type": "artifact", "atk": 40, "def": 20, "hp": 0},
    "현자의 돌": {"price": 314159265, "type": "artifact", "atk": 999, "def": 999, "hp": 999}
}

# [추가] 포션 상점 데이터
# [수정됨] 포션 상점 데이터: val 값을 퍼센트(%) 단위로 변경
# [수정됨] 포션 상점: 고정 회복량(fix) + 최대 체력 비례(pct)
POTION_SHOP = {
    "하급 포션": {
        "price": 500, "type": "potion", 
        "fix": 20, "pct": 10,  # 20 + 10%
        "desc": "체력 20 + 최대 체력의 10% 회복"
    },
    "중급 포션": {
        "price": 7500, "type": "potion", 
        "fix": 100, "pct": 30, # 100 + 20%
        "desc": "체력 100 + 최대 체력의 20% 회복"
    },
    "상급 포션": {
        "price": 30000, "type": "potion", 
        "fix": 300, "pct": 50, # 300 + 30%
        "desc": "체력 300 + 최대 체력의 30% 회복"
    },
    "엘릭서": {
        "price": 999999, "type": "potion", 
        "fix": 0, "pct": 100,  # 100% (완전 회복)
        "desc": "체력 완전 회복"
    }
}

ORES = {
    "석탄": {"emoji": "⬛", "color": 0x333333}, # 50% (첫 번째)
    "철": {"emoji": "🔘", "color": 0xaaaaaa},   # 30% (두 번째)
    "금": {"emoji": "🟡", "color": 0xffcc00},   # 15% (세 번째)
    "에메랄드": {"emoji": "💚", "color": 0x2ecc71}, # 4% (네 번째)
    "다이아몬드": {"emoji": "💎", "color": 0x3498db} # 1% (다섯 번째)
}

# [추가] 전리품 아이템 데이터
LOOT_ITEMS = {
    #----------------초보자 숲--------------
    "슬라임 점액": {"type": "loot", "price": 0, "desc": "끈적끈적한 액체다 기분이 더럽다"},
    "고블린의 뼈": {"type": "loot", "price": 0, "desc": "고블린의 피가 묻어있는 뼈다 굳이 가지고 있어야 할까?"},
    "오크의 이빨": {"type": "loot", "price": 0, "desc": "굉장한 냄새가 나는 이빨이다 당장이라도 버리고 싶다"},
    "스켈레톤의 뼈": {"type": "loot", "price": 0, "desc": "굉장히 단단해보이는 뼈다 강아지가 좋아할까?"},
    "드래곤 알": {"type": "loot", "price": 0, "desc": "커다란 알이다 이걸 구워먹으면 맛있을까?"},
    #---------------잊혀진 광산------------------
    "늑대 가죽": {"type": "loot", "price": 0, "desc": "부드러운 털가죽이다 이걸로 옷을 만들면 좋을거 같다"},
    "트롤의 피": {"type": "loot", "price": 0, "desc": "재생력이 뛰어나다 포션 재료같지만 굳이 먹고싶지 않다"},
    "이프리트의 숨결": {"type": "loot", "price": 0, "desc": "어건 어디다가 쓰는거지? 내가 순결을 뺏어버린걸까?.."},
    #---------------엘프의 숲---------------
    "엘프의 부셔진 갑옷": {"type": "loot", "price": 0, "desc": "엘프가 쓰던 갑옷이다 남이 쓰던건 좀 그렇다.."},
    "바람 추적자의 망토": {"type": "loot", "price": 0, "desc": "뭔가 좋아보이는 망토다 있으면 좋을거 같다"},
    "엘프의 왕실 문장": {"type": "loot", "price": 0, "desc": "엘리트 엘프가 가지고 있던 동그란 원판이다 이걸 어디다 쓰는거지? "},
    "수상한 빛": {"type": "loot", "price": 0, "desc": "굉장한 빛을 띄고있다.. 횟불이 필요 없을거 같다"},
    #---------------설산--------------
    "아라크네의 독이빨": {"type": "loot", "price": 0, "desc": "아주 위험해 보이는 이빨이다 양치를 안하는거 같다.."},
    "예티의 털 가죽": {"type": "loot", "price": 0, "desc": "아주 두꺼운 털 가죽이다 예티가 추워하면 어떻게 하지?"},
    "위험한 독 주머니": {"type": "loot", "price": 0, "desc": "엄청난 독을 가진 주머니다 가지고 다니기 힘들거 같다 버릴까?"},
    #--------------마왕성----------------
    "마왕의 뿔": {"type": "loot", "price": 0, "desc": "???"}
}

# 기존 ITEMS에 합치기
ITEMS.update(WEAPON_SHOP)
ITEMS.update(ARMOR_SHOP)
ITEMS.update(ARTIFACT_SHOP)
ITEMS.update(POTION_SHOP)
ITEMS.update(LOOT_ITEMS) # [추가됨]

ITEMS.update(WEAPON_SHOP)
ITEMS.update(ARMOR_SHOP)
ITEMS.update(ARTIFACT_SHOP)
ITEMS.update(POTION_SHOP) # [추가]

# [수정됨] 몬스터 데이터 (drops 정보 추가)
DUNGEON_MOBS = {
    1: {
        "mobs": {
            "슬라임": {"hp": 30, "atk": 5, "def": 2, "exp": 5, "money": 500, "image": "", "drops": [("슬라임 점액", 50), ("하급 포션", 10)]},
            "고블린": {"hp": 50, "atk": 10, "def": 4, "exp": 10, "money": 1000, "image": "", "drops": [("고블린의 뼈", 40)]},
            "오크": {"hp": 80, "atk": 15, "def": 8, "exp": 20, "money": 1500, "image": "", "drops": [("오크의 이빨", 30), ("하급 포션", 20)]},
            "스켈레톤": {"hp": 40, "atk": 20, "def": 5, "exp": 15, "money": 1200, "image": "", "drops": [("스켈레톤의 뼈", 50)]}
        },
        "boss": {
            "오염된 드래곤": {"hp": 500, "atk": 50, "def": 20, "exp": 300, "money": 50000, "image": "", "drops": [("드래곤 알", 10), ("엘릭서", 1)]}
        },
        "name": "초보자 숲"
    },
    2: {
        "mobs": {
            "늑대인간": {"hp": 200, "atk": 40, "def": 20, "exp": 40, "money": 5000, "image": "", "drops": [("늑대 가죽", 60)] },
            "트롤": {"hp": 300, "atk": 30, "def": 30, "exp": 50, "money": 7000, "image": "", "drops": [("트롤의 피", 40)]},
            "가고일": {"hp": 250, "atk": 50, "def": 40, "exp": 60, "money": 9500, "image": "", "drops": [("중급 포션", 30)]}
        },
        "boss": {
            "이프리트": {"hp": 2000, "atk": 70, "def": 50, "exp": 800, "money": 500000, "image": "", "drops": [("이프리트의 숨결", 10), ("엘릭서", 1)]}
        },
        "name": "잊혀진 광산"
    },
    3: {
        "mobs": {
            "전사 엘프": {"hp": 1000, "atk": 100, "def": 80, "exp": 300, "money": 80000, "image": "", "drops": [("엘프의 부셔진 갑옷", 50)]},
            "궁수 엘프": {"hp": 800, "atk": 200, "def": 20, "exp": 400, "money": 100000, "image": "", "drops": [("바람 추적자의 망토", 10)]},
            "엘리트 엘프": {"hp": 1500, "atk": 120, "def": 100, "exp": 500, "money": 150000, "image": "", "drops": [("엘프의 왕실 문장", 50)]}
        },
        "boss": {
            "심연에 잠든 고대정령": {"hp": 5000, "atk": 500, "def": 300, "exp": 5000, "money": 1000000, "image": "", "drops": [("수상한 빛", 10),("엘릭서", 1)]}
        },
        "name": "엘프의 숲"
    },
    4: {
        "mobs": {
            "빙결의 아라크네": {"hp": 3000, "atk": 250, "def": 150, "exp": 1200, "money": 300000, "image": "", "drops": [("아라크네의 독이빨", 50)]},
            "파왕 예티": {"hp": 6000, "atk": 200, "def": 200, "exp": 1600, "money": 500000, "image": "", "drops": [("예티의 털 가죽", 20)]},
            "서리 새끼거미 무리": {"hp": 3500, "atk": 500, "def": 20, "exp": 2000, "money": 400000, "image": "", "drops": [("상급 포션", 50)]}
        },
        "boss": {
            "수정 동굴의 여왕": {"hp": 10000, "atk": 900, "def": 300, "exp": 20000, "money": 5000000, "image": "", "drops": [("위험한 독 주머니", 10),("엘릭서", 1)]}
        },
        "name": "설산"
    }
    
}

# 기존 몬스터 데이터 호환성 유지 (에러 방지용)
MONSTERS = DUNGEON_MOBS[1]["mobs"].copy()
MONSTERS.update(DUNGEON_MOBS[1]["boss"])



# ---------------- 2. 데이터 관리 및 RPG 로직 ----------------
def load_inv():
    if not os.path.exists(INV_FILE): return {}
    with open(INV_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_inv(data):
    with open(INV_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

# [수정됨] 유저 생성 시 'loot' 인벤토리 추가
def create_user_if_not_exists(user_id):
    data = load_inv()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "inventory": {"weapon": ["낡은 목검"], "armor": ["가죽 갑옷"], "artifact": ["금간 철 반지"], "potion": [], "loot": []},
            "equipped": {"weapon": "낡은 목검", "armor": "가죽 갑옷", "artifact": "금간 철 반지"},
            "level": 1, "exp": 0, "point": 0,
            "added_atk": 0, "added_def": 0, "added_hp": 0
        }
        save_inv(data)
    
    # [호환성] 기존 유저에게 potion이나 loot 칸이 없으면 생성
    changed = False
    if "potion" not in data[uid]["inventory"]:
        data[uid]["inventory"]["potion"] = []; changed = True
    if "loot" not in data[uid]["inventory"]:
        data[uid]["inventory"]["loot"] = []; changed = True
        
    for key in ["point", "added_atk", "added_def", "added_hp"]:
        if key not in data[uid]: data[uid][key] = 0; changed = True
        
    if changed: save_inv(data)
    return data[uid]





# [수정됨] 아이템 이름에서 강화 수치 (+N)를 분리하고 스탯 계산
def parse_item(name):
    match = re.search(r'\(\+(\d+)\)', name)
    if match:
        level = int(match.group(1))
        real_name = name.replace(f" (+{level})", "")
        return real_name, level
    return name, 0

# [수정됨] 강화 스탯 계산: 고정 수치(+2)가 아니라 원본 능력치의 10%씩 증가
def calculate_stats(user_id):
    
    data = load_inv()
    uid = str(user_id)
    if uid not in data: return BASE_STATS["atk"], BASE_STATS["def"], BASE_STATS["hp"]
    
    
    user = data[uid]
    eq = user.get("equipped", {})
    
    atk = BASE_STATS["atk"] + user.get("added_atk", 0)
    dfe = BASE_STATS["def"] + user.get("added_def", 0)
    hp = BASE_STATS["hp"] + user.get("added_hp", 0)
    
    for slot in ["weapon", "armor", "artifact"]:
        full_name = eq.get(slot)
        if not full_name: continue
        
        name, level = parse_item(full_name)
        item = ITEMS.get(name)
        
        if item:
            # 기본 능력치 더하기
            i_atk = item.get("atk", 0)
            i_def = item.get("def", 0)
            i_hp = item.get("hp", 0)
            
            atk += i_atk
            dfe += i_def
            hp += i_hp
            
            # [변경점] 강화 보너스: (기본 능력치 * 0.1 * 레벨)
            # 소수점은 버림(int) 처리
            if level > 0:
                atk += int(i_atk * 0.1 * level)
                dfe += int(i_def * 0.1 * level)
                hp += int(i_hp * 0.1 * level)
            
    return atk, dfe, hp

def required_exp(level):
    if level <= 10:
        return 50 + (level * 100)
    else:
        return 50 + (level * 100) + (level * level * 10)

# ---------------- 3. 클라이언트 설정 ----------------
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self): await self.tree.sync()

client = MyClient()
last_used = {}
COOLDOWN = 600

# [추가] 던전용 쿨타임 변수 (30초)
dungeon_last_used = {}
DUNGEON_COOLDOWN = 30

# ---------------- 4. UI 클래스 ----------------

# [수정됨] 상점 선택 로직: 포션은 모달 띄우기, 장비는 즉시 구매
# [1. 새로 추가됨] 수량 입력 모달 창 (이게 위에 있어야 합니다!)
class BuyAmountModal(discord.ui.Modal):
    def __init__(self, item_name, item_info):
        super().__init__(title=f"{item_name} 구매")
        self.item_name = item_name
        self.item_info = item_info
        # 입력창 설정
        self.amount = discord.ui.TextInput(label="몇 개 구매할 거냐?", placeholder="숫자를 입력해라 (예: 10)", min_length=1, max_length=3)
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.amount.value)
            if count <= 0: raise ValueError
        except:
            return await interaction.response.send_message("장난치지 마라! 자연수만 입력해라.", ephemeral=True)

        price = self.item_info["price"]
        total_price = price * count
        uid = str(interaction.user.id)

        m_data = load_data()
        money = m_data.get(uid, 0)

        if money < total_price:
            return await interaction.response.send_message(f"돈이 부족하다라! (필요: {total_price:,}원 / 보유: {money:,}원)", ephemeral=True)

        inv_data = load_inv()
        create_user_if_not_exists(uid)

        # 돈 차감
        m_data[uid] -= total_price
        
        # [중요] 포션 리스트에 개수만큼 추가 (extend 사용)
        inv_data[uid]["inventory"]["potion"].extend([self.item_name] * count)
        
        save_data(m_data)
        save_inv(inv_data)

        embed = discord.Embed(title="✅ 구매 성공", description=f"**{self.item_name}** {count}개를 구매했다라!\n총 지출: **{total_price:,}원**", color=0x2ecc71)
        await interaction.response.send_message(embed=embed)

class MiningView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = str(user_id)
        
        # 1. 광석 랜덤 뽑기 (확률 조정)
        # weights 숫자가 클수록 잘 나옴 (석탄 > 철 > 금 > 에메랄드 > 다이아)
        ore_names = list(ORES.keys())
        selected_ore = random.choices(ore_names, weights=[40, 30, 20, 8, 2], k=1)[0]
        
        self.ore_name = selected_ore
        self.ore_data = ORES[selected_ore]
        
        # 2. 체력 설정 (무조건 10)
        self.max_hp = 10
        self.current_hp = 10

    def get_embed(self):
        # 체력바 만들기 (예: 🟥🟥🟥🟥🟥⬜⬜⬜⬜⬜)
        percent = int((self.current_hp / self.max_hp) * 10)
        bar = "🟩" * percent + "⬜" * (10 - percent)
        
        embed = discord.Embed(
            title=f"⛏️ 광질 중... [{self.ore_name}] 발견!",
            description="곡괭이로 두들겨서 광석을 캐라!",
            color=self.ore_data["color"]
        )
        embed.add_field(name=f"{self.ore_data['emoji']} {self.ore_name}", value=f"내구도: {self.current_hp}/{self.max_hp}\n{bar}", inline=False)
        embed.set_footer(text="버튼을 10번 눌러야 한다라!")
        return embed

    @discord.ui.button(label="캐기!", style=discord.ButtonStyle.primary, emoji="⛏️")
    async def mine(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("내 광물이다라! 건들지 마라!", ephemeral=True)
        
        # 3. 채굴 로직 (데미지 무조건 1)
        self.current_hp -= 1
        
        if self.current_hp > 0:
            # 아직 안 깨짐 -> 임베드 업데이트
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            # 깨짐! -> 보상 지급 및 종료
            m_data = load_data()
            reward = self.ore_data["money"]
            m_data[self.user_id] = m_data.get(self.user_id, 0) + reward
            save_data(m_data)
            
            # 성공 메시지
            embed = discord.Embed(
                title=f"✨ 채굴 성공!",
                description=f"**{self.ore_name}**을(를) 캐서 **{reward:,}원**을 벌었다라!",
                color=self.ore_data["color"]
            )
            embed.set_thumbnail(url="https://emojigraph.org/media/apple/pick_26cf-fe0f.png") # 곡괭이 이미지 (선택)
            
            # 버튼 비활성화 (모든 버튼 끄기)
            for child in self.children:
                child.disabled = True
                
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()

# [2. 수정됨] 상점 선택 로직 (포션은 모달 띄우기, 장비는 즉시 구매)
# [1. 새로 추가됨] 수량 입력 모달 창 (이게 위에 있어야 합니다!)
class BuyAmountModal(discord.ui.Modal):
    def __init__(self, item_name, item_info):
        super().__init__(title=f"{item_name} 구매")
        self.item_name = item_name
        self.item_info = item_info
        # 입력창 설정
        self.amount = discord.ui.TextInput(label="몇 개 구매할 거냐?", placeholder="숫자를 입력해라 (예: 10)", min_length=1, max_length=3)
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.amount.value)
            if count <= 0: raise ValueError
        except:
            return await interaction.response.send_message("장난치지 마라! 자연수만 입력해라.", ephemeral=True)

        price = self.item_info["price"]
        total_price = price * count
        uid = str(interaction.user.id)

        m_data = load_data()
        money = m_data.get(uid, 0)

        if money < total_price:
            return await interaction.response.send_message(f"돈이 부족하다라! (필요: {total_price:,}원 / 보유: {money:,}원)", ephemeral=True)

        inv_data = load_inv()
        create_user_if_not_exists(uid)

        # 돈 차감
        m_data[uid] -= total_price
        
        # [중요] 포션 리스트에 개수만큼 추가 (extend 사용)
        inv_data[uid]["inventory"]["potion"].extend([self.item_name] * count)
        
        save_data(m_data)
        save_inv(inv_data)

        embed = discord.Embed(title="✅ 구매 성공", description=f"**{self.item_name}** {count}개를 구매했다라!\n총 지출: **{total_price:,}원**", color=0x2ecc71)
        await interaction.response.send_message(embed=embed)


# [2. 수정됨] 상점 선택 로직 (포션은 모달 띄우기, 장비는 즉시 구매)
class UniversalShopSelect(discord.ui.Select):
    def __init__(self, shop_name, item_list):
        self.item_list = item_list
        options = []
        for n, i in item_list.items():
            # 설명에 가격과 효과를 같이 표시
            desc_text = i.get('desc', "")
            if i['type'] == 'potion':
                desc = f"{i['price']:,}원 | {desc_text}"
            else:
                desc = f"{i['price']:,}원"
                
            options.append(discord.SelectOption(label=n, description=desc, value=n))
        super().__init__(placeholder=f"{shop_name}에서 물건을 골라라!", options=options)

    async def callback(self, interaction: discord.Interaction):
        item_name = self.values[0]
        item_info = self.item_list[item_name]
        i_type = item_info["type"]
        
        # [핵심] 포션이면 방금 만든 모달 띄우기
        if i_type == "potion":
            await interaction.response.send_modal(BuyAmountModal(item_name, item_info))
            return

        # --- 아래는 기존 장비 구매 로직 (1개만 구매) ---
        price = item_info["price"]
        uid = str(interaction.user.id)
        
        m_data = load_data()
        money = m_data.get(uid, 0)

        if money < price:
            embed = discord.Embed(title="❌ 구매 실패", description=f"돈이 부족하다라!\n보유: **{money:,}원** / 필요: **{price:,}원**", color=0xe74c3c)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        inv_data = load_inv()
        create_user_if_not_exists(uid)
        
        # 장비는 중복 구매 불가 체크
        if item_name not in inv_data[uid]["inventory"][i_type]:
            m_data[uid] = money - price
            inv_data[uid]["inventory"][i_type].append(item_name)
            save_data(m_data); save_inv(inv_data)
            embed = discord.Embed(title="✅ 구매 완료", description=f"**{item_name}**을(를) 구매했다라!\n남은 잔액: **{m_data[uid]:,}원**", color=0x2ecc71)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("이미 가지고 있는 장비다라! (장비는 중복 구매 불가)", ephemeral=True)

# [추가] 전투 중 포션 선택 메뉴
# [수정됨] 전투 중 포션 선택 메뉴
class BattlePotionSelect(discord.ui.View):
    def __init__(self, dungeon_view, user_potions):
        super().__init__(timeout=60)
        self.dungeon_view = dungeon_view
        
        # 포션 개수 세기
        counts = Counter(user_potions)
        options = []
        for name, count in counts.items():
            info = ITEMS.get(name, {})
            # 설명 가져오기 (없으면 기본값)
            desc = info.get("desc", "체력 회복")
            
            options.append(discord.SelectOption(
                label=f"{name} (보유: {count}개)",
                description=desc,
                value=name
            ))
            
        self.add_item(PotionSelectMenu(options, dungeon_view))

class PotionSelectMenu(discord.ui.Select):
    def __init__(self, options, dungeon_view):
        super().__init__(placeholder="사용할 포션을 선택하세요", options=options)
        self.dungeon_view = dungeon_view

    async def callback(self, interaction: discord.Interaction):
        item_name = self.values[0]
        uid = str(interaction.user.id)
        
        # 인벤토리에서 하나 삭제
        data = load_inv()
        if item_name in data[uid]["inventory"]["potion"]:
            data[uid]["inventory"]["potion"].remove(item_name)
            save_inv(data)
            
            # 던전 뷰의 포션 사용 함수 호출
            heal = ITEMS[item_name]["val"]
            await self.dungeon_view.use_potion_effect(interaction, item_name, heal)
        else:
            await interaction.response.send_message("포션이 없다라?! (오류)", ephemeral=True)

class DungeonView(discord.ui.View):
    def __init__(self, interaction, user_id, dungeon_level=1):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.user_id = str(user_id)
        self.dungeon_level = dungeon_level
        self.dungeon_data = DUNGEON_MOBS[dungeon_level]
        
        self.atk, self.dfe, self.max_hp = calculate_stats(user_id)
        self.current_hp = self.max_hp
        self.stage = 1
        self.max_stage = 10
        
        # [추가됨] 포션 사용 횟수 카운트 초기화
        self.potion_used_count = 0 
        
        self.log = f"**[{self.dungeon_data['name']}]**에 입장했다라! 조심해라!"
        self.spawn_monster()

    def spawn_monster(self):
        # 10층이면 보스, 아니면 일반 몬스터 소환
        if self.stage == self.max_stage:
            # 보스 딕셔너리에서 하나 가져옴
            name, stat = random.choice(list(self.dungeon_data["boss"].items()))
            self.monster_name = name
            self.monster = stat.copy()
            self.is_boss = True
        else:
            name, stat = random.choice(list(self.dungeon_data["mobs"].items()))
            self.monster_name = name
            self.monster = stat.copy()
            self.is_boss = False
            
        self.monster_max_hp = self.monster["hp"]

    async def update_battle(self, interaction=None):
        p_per = max(0, int((self.current_hp / self.max_hp) * 10))
        m_per = max(0, int((self.monster["hp"] / self.monster_max_hp) * 10))
        player_bar = "🟩" * p_per + "⬜" * (10 - p_per)
        monster_bar = "🟥" * m_per + "⬜" * (10 - m_per)
        
        # 보스전이거나 던전 레벨이 높으면 색상 변경
        color = 0x992d22 if self.is_boss else (0xe74c3c if self.dungeon_level == 1 else 0x9b59b6)
        
        embed = discord.Embed(title=f"🏰 {self.dungeon_data['name']} [{self.stage}/{self.max_stage}층] : {self.monster_name}", color=color)
        if self.monster.get("image"): embed.set_thumbnail(url=self.monster["image"])
        embed.add_field(name=f"😈 {self.monster_name}", value=f"HP: {self.monster['hp']}/{self.monster_max_hp}\n{monster_bar}", inline=False)
        embed.add_field(name=f"🛡️ {self.interaction.user.name}", value=f"HP: {self.current_hp}/{self.max_hp}\n{player_bar}", inline=False)
        embed.add_field(name="📜 전투 로그", value=f"```\n{self.log}\n```", inline=False)

        target = interaction if interaction else self.interaction
        try:
            if target.response.is_done(): await target.edit_original_response(embed=embed, view=self)
            else: await target.response.edit_message(embed=embed, view=self)
        except: pass

    @discord.ui.button(label="공격", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id: return
        dmg = max(1, (self.atk - self.monster["def"]) + random.randint(-2, 2))
        self.monster["hp"] -= dmg
        self.log = f"🗡️ {self.monster_name}에게 {dmg} 데미지!"

        if self.monster["hp"] <= 0: return await self.stage_clear(interaction)
        
        mob_dmg = max(1, (self.monster["atk"] - self.dfe) + random.randint(-1, 1))
        self.current_hp -= mob_dmg
        self.log += f"\n💥 윽! {mob_dmg} 데미지를 입었다라!"

        if self.current_hp <= 0: return await self.game_over(interaction)
        await self.update_battle(interaction)

    # [수정] 포션 버튼: 누르면 선택 메뉴 띄움 (기존 '포션 사용' 버튼 대체)
    @discord.ui.button(label="아이템 사용", style=discord.ButtonStyle.success, emoji="🧪")
    async def open_potion_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id: return
        
        # [추가됨] 5회 이상 사용 시 사용 불가 처리
        if self.potion_used_count >= 5:
            return await interaction.response.send_message(f"❌ 배가 불러서 더 못 마신다라! (사용 제한: 5회 끝)", ephemeral=True)

        data = load_inv()
        potions = data[self.user_id]["inventory"].get("potion", [])
        
        if not potions:
            return await interaction.response.send_message("🧪 가진 포션이 하나도 없다라!", ephemeral=True)
            
        # 몇 개 썼는지 알려주면서 메뉴 열기
        view = BattlePotionSelect(self, potions)
        await interaction.response.send_message(f"사용할 포션을 골라라! (현재 {self.potion_used_count}/5 사용)", view=view, ephemeral=True)

    # [추가] 실제 포션 사용 효과 처리 함수
    # [수정됨] 실제 포션 사용 효과 처리 함수 (하이브리드 공식 적용)
    async def use_potion_effect(self, interaction, item_name, temp_val=None):
        item_info = ITEMS.get(item_name)
        if not item_info: return

        # [추가됨] 사용 횟수 1 증가
        self.potion_used_count += 1

        prev_hp = self.current_hp
        
        # 공식: 고정 회복량 + (최대 체력 * 퍼센트 / 100)
        fix_heal = item_info.get("fix", 0)
        pct_heal = int(self.max_hp * (item_info.get("pct", 0) / 100))
        total_heal = fix_heal + pct_heal
        
        self.current_hp = min(self.max_hp, self.current_hp + total_heal)
        real_heal = self.current_hp - prev_hp
        
        mob_dmg = max(1, (self.monster["atk"] - self.dfe))
        self.current_hp -= mob_dmg
        
        # [추가됨] 로그에 (현재 사용 횟수/5) 표시
        self.log = f"🧪 **{item_name}** 사용! ({self.potion_used_count}/5)\n(체력 {real_heal} 회복)\n💥 꿀꺽하는 동안 {mob_dmg} 데미지를 입었다라!"
        
        if self.current_hp <= 0:
            await self.game_over(interaction)
        else:
            await self.update_battle(interaction)

    @discord.ui.button(label="도망", style=discord.ButtonStyle.secondary, emoji="🏃")
    async def run(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id: return
        if self.stage == self.max_stage:
            self.log = "🚫 보스에게서는 도망칠 수 없다라!"
            return await self.update_battle(interaction)

        self.log = "🏃 던전에서 도망쳤다라..."
        await interaction.response.edit_message(content="🏃💨 던전 포기! 마을로 돌아갑니다라.", embed=None, view=None)
        self.stop()

    # [수정됨] 스테이지 클리어 (경험치/골드 표시 추가)
    # [수정됨] 스테이지 클리어 (전리품 획득 로직 추가)
    async def stage_clear(self, interaction):
        reward_money = self.monster["money"]
        reward_exp = self.monster["exp"]
        
        data = load_data(); inv = load_inv()
        
        # 1. 돈과 경험치 지급
        data[self.user_id] = data.get(self.user_id, 0) + reward_money
        inv[self.user_id]["exp"] += reward_exp
        
        # 2. 전리품(드랍) 계산
        drop_msg = ""
        drops = self.monster.get("drops", []) # 몬스터의 드랍 테이블 가져오기
        
        for item_name, rate in drops:
            # 1~100 사이 랜덤 숫자가 확률보다 낮으면 획득
            if random.randint(1, 100) <= rate:
                # 아이템 타입 확인 (전리품인지, 포션인지 등)
                itype = ITEMS.get(item_name, {}).get("type", "loot")
                
                # 인벤토리에 추가
                if itype not in inv[self.user_id]["inventory"]:
                    inv[self.user_id]["inventory"][itype] = []
                inv[self.user_id]["inventory"][itype].append(item_name)
                
                drop_msg += f"\n🎁 **{item_name}** 획득!"

        save_data(data); save_inv(inv)

        # 3. 결과 출력 및 다음 층 이동
        if self.stage >= self.max_stage:
            embed = discord.Embed(title="🏆 던전 정복 완료!", description=f"전설적인 몬스터 **{self.monster_name}**을(를) 쓰러뜨렸다라!", color=0xf1c40f)
            embed.add_field(name="최종 보상", value=f"💰 {reward_money * 3}원 (보너스)\n✨ {reward_exp * 3} EXP{drop_msg}")
            
            # 보스 추가 보상
            data[self.user_id] += reward_money * 2
            inv[self.user_id]["exp"] += reward_exp * 2
            save_data(data); save_inv(inv)
            
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
        else:
            self.stage += 1
            heal = int(self.max_hp * 0.3)
            self.current_hp = min(self.max_hp, self.current_hp + heal)
            
            reward_text = f"[ 💰+{reward_money}G | ✨+{reward_exp}EXP ]"
            self.log = f"✅ {self.monster_name} 처치! {reward_text}{drop_msg}\n💤 휴식하여 체력이 {heal} 회복되었다라.\n곧바로 {self.stage}층으로 이동한다라!"
            
            self.spawn_monster()
            await self.update_battle(interaction)

    async def game_over(self, interaction):
        embed = discord.Embed(title="💀 게임 오버", description=f"{self.stage}층에서 쓰러졌다라... 마을로 귀환한다라.", color=0x2c3e50)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

# ---------------- 4. UI 클래스 (인벤토리 관련 수정됨) ----------------

# [수정됨] 인벤토리 화면을 만들어주는 함수
def create_inventory_embed(user, uid, cat):
    data = load_inv()
    
    # ★ 이 부분이 핵심입니다! "loot": "전리품" 이 꼭 있어야 해요! ★
    names = {"weapon": "무기", "armor": "갑옷", "artifact": "아티팩트", "potion": "포션", "loot": "전리품"}
    
    # 카테고리 이름 가져오기
    cat_name = names.get(cat, cat)
    
    embed = discord.Embed(title=f"🎒 {user.name}의 인벤토리", description=f"현재 **[{cat_name}]** 목록이다라!", color=0x3498db)
    
    # 포션이나 전리품은 '개수'로 묶어서 보여줌
    if cat in ["potion", "loot"]:
        items = data[uid]["inventory"].get(cat, [])
        if items:
            counts = Counter(items)
            val = "\n".join([f"- {n}: **{c}개**" for n, c in counts.items()])
        else: 
            val = "비어있다라."
    else:
        # 장비류 (기존 로직)
        inv = data[uid]["inventory"].get(cat, [])
        eq = data[uid]["equipped"].get(cat, "없음")
        inv_list = []
        for item_name in inv:
            item_info = ITEMS.get(item_name, {})
            equipped_mark = " **(장착 중)**" if item_name == eq else ""
            inv_list.append(f"- {item_name}{equipped_mark}")
        val = "\n".join(inv_list) if inv_list else "아이템이 없다라."
        
    embed.add_field(name="보유 목록", value=val, inline=False)
    atk, dfe, hp = calculate_stats(uid)
    embed.set_footer(text=f"현재 총 능력치: ⚔️{atk} 🛡️{dfe} ❤️{hp}")
    return embed
    

# [수정됨] 인벤토리 버튼 및 드롭다운 클래스
class InventoryView(discord.ui.View):
    def __init__(self, user_id, category="weapon"):
        super().__init__(timeout=60)
        self.user_id = str(user_id)
        self.category = category

    def create_options(self):
        data = load_inv()
        user_data = data.get(self.user_id, {})
        
        # [수정됨] 포션과 전리품 처리
        if self.category in ["potion", "loot"]:
            items = user_data.get("inventory", {}).get(self.category, [])
            if not items: 
                return [discord.SelectOption(label="비어 있음", value="none", description="가진 아이템이 없다라!")]
            
            # 개수 세기
            counts = Counter(items)
            options = []
            for n, c in counts.items():
                desc = ITEMS.get(n, {}).get("desc", "아이템")
                options.append(discord.SelectOption(label=f"{n} ({c}개)", value=n, description=desc))
            return options[:25]

        # [기존 로직] 장비류
        items = user_data.get("inventory", {}).get(self.category, [])
        eq = user_data.get("equipped", {}).get(self.category)
        
        if not items: 
            return [discord.SelectOption(label="비어 있음", value="none", description="가진 아이템이 없다라!")]
        
        options = []
        for n in items:
            is_equipped = "(장착중)" if n == eq else ""
            item_info = ITEMS.get(n, {}) 
            stats = []
            if item_info.get("atk", 0) > 0: stats.append(f"ATK+{item_info['atk']}")
            if item_info.get("def", 0) > 0: stats.append(f"DEF+{item_info['def']}")
            if item_info.get("hp", 0) > 0: stats.append(f"HP+{item_info['hp']}")
            stat_str = " / ".join(stats) if stats else "능력치 없음"
            options.append(discord.SelectOption(label=f"{n} {is_equipped}", value=n, description=stat_str))
        return options[:25]

    @discord.ui.select(placeholder="아이템 선택")
    async def select_item(self, interaction: discord.Interaction, select: discord.ui.Select):
        if str(interaction.user.id) != self.user_id: return
        val = select.values[0]
        if val == "none": return await interaction.response.defer()
        
        # [수정됨] 포션/전리품 장착 불가 처리
        if self.category in ["potion", "loot"]:
            return await interaction.response.send_message(f"**{val}**은(는) 장착하는 아이템이 아니다라!", ephemeral=True)

        data = load_inv()
        data[self.user_id]["equipped"][self.category] = val
        save_inv(data)
        await interaction.response.send_message(f"✅ **{val}** 장착 완료!", ephemeral=True)
        await self.refresh(interaction)

    # 버튼들 (row 값으로 줄 바꿈)
    @discord.ui.button(label="🗡️ 무기", style=discord.ButtonStyle.gray, row=0)
    async def btn_w(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.category = "weapon"
        await self.refresh(interaction)

    @discord.ui.button(label="🛡️ 갑옷", style=discord.ButtonStyle.gray, row=0)
    async def btn_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.category = "armor"
        await self.refresh(interaction)

    @discord.ui.button(label="💍 아티팩트", style=discord.ButtonStyle.gray, row=0)
    async def btn_r(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.category = "artifact"
        await self.refresh(interaction)
        
    @discord.ui.button(label="🧪 포션", style=discord.ButtonStyle.gray, row=1)
    async def btn_p(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.category = "potion"
        await self.refresh(interaction)

    @discord.ui.button(label="📦 전리품", style=discord.ButtonStyle.gray, row=1)
    async def btn_loot(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.category = "loot"
        await self.refresh(interaction)

    async def refresh(self, interaction: discord.Interaction):
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                item.options = self.create_options()
        
        # 여기서 에러가 났던 겁니다 (cat='loot'를 처리 못해서)
        embed = create_inventory_embed(interaction.user, self.user_id, self.category)
        
        if interaction.response.is_done(): 
            await interaction.edit_original_response(embed=embed, view=self)
        else: 
            await interaction.response.edit_message(embed=embed, view=self)

# [수정됨] 인벤토리 화면을 만들어주는 함수 (loot 키가 추가됨!)


class StatButton(discord.ui.View):
    def __init__(self, uid): super().__init__(timeout=60); self.uid = str(uid)
    async def add_s(self, interaction, key):
        if str(interaction.user.id) != self.uid: return
        data = load_inv()
        if data[self.uid]["point"] <= 0: return await interaction.response.send_message("포인트 부족!", ephemeral=True)
        data[self.uid]["point"] -= 1
        data[self.uid][key] += (10 if key=="added_hp" else 1)
        save_inv(data); await stats_callback(interaction, self.uid)

# ---------------- [추가] 장비 강화 시스템 ----------------

# [수정됨] 강화 시스템 (가격 공식 변경: 원가 비례 10% ~ 100%+)
class EnhanceView(discord.ui.View):
    def __init__(self, user_id, category):
        super().__init__(timeout=60)
        self.user_id = str(user_id)
        self.category = category
        self.options = self.get_enhance_options()
        if self.options:
            self.add_item(EnhanceSelect(self.options))

    def get_enhance_options(self):
        data = load_inv()
        items = data[self.user_id]["inventory"].get(self.category, [])
        if not items: return []
        
        unique_items = sorted(list(set(items)))
        
        options = []
        for name in unique_items:
            # 1. 정보 파싱
            real_name, level = parse_item(name)
            item_info = ITEMS.get(real_name, {})
            base_price = item_info.get("price", 0) # 아이템 원가 가져오기
            
            # 2. [변경점] 강화 비용 계산 (원가 * (강화레벨+1) * 10%)
            # 예: 0강->1강(10%), 1강->2강(20%) ... 9강->10강(100%)
            cost = int(base_price * (level + 1) * 0.1)
            
            # 최소 비용 100원 보정 (너무 싸면 재미없으니까)
            if cost < 100: cost = 100
            
            prob = max(10, 100 - (level * 10)) # 성공 확률
            
            options.append(discord.SelectOption(
                label=f"{name}", 
                description=f"비용: {cost:,}원 | 성공확률: {prob}%", 
                value=name
            ))
        return options[:25]

class EnhanceSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="강화할 장비를 선택해라!", options=options)

    async def callback(self, interaction: discord.Interaction):
        item_full_name = self.values[0]
        uid = str(interaction.user.id)
        
        # 1. 정보 파싱
        real_name, level = parse_item(item_full_name)
        item_info = ITEMS.get(real_name)
        
        if not item_info: 
            return await interaction.response.send_message("존재하지 않는 아이템이다라!", ephemeral=True)
            
        base_price = item_info.get("price", 0)
        
        # 2. [변경점] 비용 계산 (View랑 똑같은 공식 적용)
        cost = int(base_price * (level + 1) * 0.1)
        if cost < 100: cost = 100
        
        prob = max(10, 100 - (level * 10))
        
        # 3. 돈 확인
        data = load_data()
        money = data.get(uid, 0)
        
        if money < cost:
            return await interaction.response.send_message(f"돈이 부족하다라! (필요: {cost:,}원)", ephemeral=True)
            
        # 4. 강화 시도
        inv_data = load_inv()
        category = item_info["type"]
        
        if item_full_name not in inv_data[uid]["inventory"][category]:
            return await interaction.response.send_message("아이템이 사라졌다라?!", ephemeral=True)

        # 돈 차감
        data[uid] -= cost
        save_data(data)
        
        # 확률 돌리기
        rand = random.randint(1, 100)
        
        if rand <= prob:
            # [성공]
            inv_data[uid]["inventory"][category].remove(item_full_name)
            
            next_level = level + 1
            new_name = f"{real_name} (+{next_level})"
            inv_data[uid]["inventory"][category].append(new_name)
            
            # 장착 중이면 이름 변경
            if inv_data[uid]["equipped"].get(category) == item_full_name:
                inv_data[uid]["equipped"][category] = new_name
                
            save_inv(inv_data)
            
            embed = discord.Embed(title="🔨 강화 성공!", description=f"**{new_name}** (으)로 강화되었다라!\n(비용 -{cost:,}원)", color=0x2ecc71)
            await interaction.response.send_message(embed=embed)
        else:
            # [실패]
            embed = discord.Embed(title="💥 강화 실패...", description=f"손이 미끄러졌다라...\n(돈만 날렸다라 -{cost:,}원)", color=0xe74c3c)
            await interaction.response.send_message(embed=embed)

# [수정됨] 실제 강화 버튼을 눌렀을 때 처리하는 부분 (가격 공식 수정)
class EnhanceSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="강화할 장비를 선택해라!", options=options)

    async def callback(self, interaction: discord.Interaction):
        item_full_name = self.values[0]
        uid = str(interaction.user.id)
        
        # 1. 정보 파싱
        real_name, level = parse_item(item_full_name)
        item_info = ITEMS.get(real_name)
        
        if not item_info: 
            return await interaction.response.send_message("존재하지 않는 아이템이다라!", ephemeral=True)
            
        base_price = item_info.get("price", 0)
        
        # ★ [여기가 문제였음] ★
        # 옛날 공식: cost = (level + 1) * 1000 
        # 바뀐 공식: 원가의 10% (최소 100원)
        cost = int(base_price * (level + 1) * 0.1)
        if cost < 100: cost = 100
        
        prob = max(10, 100 - (level * 10))
        
        # 3. 돈 확인
        data = load_data()
        money = data.get(uid, 0)
        
        if money < cost:
            return await interaction.response.send_message(f"돈이 부족하다라! (필요: {cost:,}원)", ephemeral=True)
            
        # 4. 강화 시도
        inv_data = load_inv()
        category = item_info["type"]
        
        if item_full_name not in inv_data[uid]["inventory"][category]:
            return await interaction.response.send_message("아이템이 사라졌다라?!", ephemeral=True)

        # 돈 차감
        data[uid] -= cost
        save_data(data)
        
        # 확률 돌리기
        rand = random.randint(1, 100)
        
        if rand <= prob:
            # [성공]
            inv_data[uid]["inventory"][category].remove(item_full_name)
            
            next_level = level + 1
            new_name = f"{real_name} (+{next_level})"
            inv_data[uid]["inventory"][category].append(new_name)
            
            # 장착 중이면 이름 변경
            if inv_data[uid]["equipped"].get(category) == item_full_name:
                inv_data[uid]["equipped"][category] = new_name
                
            save_inv(inv_data)
            
            embed = discord.Embed(title="🔨 강화 성공!", description=f"**{new_name}** (으)로 강화되었다라!\n(비용 -{cost:,}원)", color=0x2ecc71)
            await interaction.response.send_message(embed=embed)
        else:
            # [실패]
            embed = discord.Embed(title="💥 강화 실패...", description=f"손이 미끄러졌다라...\n(돈만 날렸다라 -{cost:,}원)", color=0xe74c3c)
            await interaction.response.send_message(embed=embed)

# ---------------- 5. 명령어 섹션 ----------------
@client.event
async def on_ready(): print(f"로그인 완료: {client.user}")

@client.tree.command(name="돈내놔", description="5000원을 받습니다라!")
async def give_money(interaction: discord.Interaction):
    uid = str(interaction.user.id); now = time.time()
    if uid in last_used and now - last_used[uid] < COOLDOWN:
        return await interaction.response.send_message(f"⏳ 쿨타임 중이다라! 남은 시간: **{int(COOLDOWN-(now-last_used[uid]))}초**", ephemeral=True)
    last_used[uid] = now
    data = load_data(); data[uid] = data.get(uid, 0) + 5000; save_data(data)
    embed = discord.Embed(title="💰 돈 지급 완료", description=f"**5,000원**을 받았다라!\n현재 잔액: **{data[uid]:,}원**", color=0x2ecc71)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="지갑", description="잔고를 확인한다라!")
async def wallet(interaction: discord.Interaction):
    data = load_data(); uid = str(interaction.user.id); money = data.get(uid, 0)
    sorted_u = sorted(data.items(), key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (u, _) in enumerate(sorted_u) if u == uid), "N/A")
    embed = discord.Embed(title="👛 내 지갑", color=0x2ecc71)
    embed.add_field(name="보유 잔액", value=f"**{money:,}원**", inline=True)
    embed.add_field(name="재력 순위", value=f"**{rank}위**", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="무기상점", description="무기를 파는 곳 이다라!")
async def w_shop(i):
    embed = discord.Embed(title="⚔️ 무기 상점", description="강력한 무기들을 판매한다라!", color=0x95a5a6)
    for n, i_info in WEAPON_SHOP.items(): embed.add_field(name=n, value=f"가격: {i_info['price']:,}원 | ATK +{i_info['atk']} DEF +{i_info['def']} / HP +{i_info['hp']}", inline=False)
    v = discord.ui.View(); v.add_item(UniversalShopSelect("무기상점", WEAPON_SHOP))
    await i.response.send_message(embed=embed, view=v)

@client.tree.command(name="갑옷상점", description="갑옷을 파는 곳 이다라!")
async def a_shop(i):
    embed = discord.Embed(title="🛡️ 갑옷 상점", description="튼튼한 방어구를 판매한다라!", color=0x34495e)
    for n, i_info in ARMOR_SHOP.items(): embed.add_field(name=n, value=f"가격: {i_info['price']:,}원 | ATK +{i_info['atk']} DEF +{i_info['def']} / HP +{i_info['hp']}", inline=False)
    v = discord.ui.View(); v.add_item(UniversalShopSelect("갑옷상점", ARMOR_SHOP))
    await i.response.send_message(embed=embed, view=v)

@client.tree.command(name="아티팩트상점", description="아티펙트를 파는 곳 이다라!")
async def r_shop(i):
    embed = discord.Embed(title="💍 아티팩트 상점", description="신비한 장신구를 판매한다라!", color=0x9b59b6)
    for n, i_info in ARTIFACT_SHOP.items(): embed.add_field(name=n, value=f"가격: {i_info['price']:,}원 | ATK +{i_info['atk']} DEF +{i_info['def']} / HP +{i_info['hp']}" , inline=False)
    v = discord.ui.View(); v.add_item(UniversalShopSelect("아티팩트상점", ARTIFACT_SHOP))
    await i.response.send_message(embed=embed, view=v)

# [추가] 포션 상점 명령어
@client.tree.command(name="포션상점", description="체력 물약을 파는 곳 이다라!")
async def p_shop(i):
    embed = discord.Embed(title="🧪 포션 상점", description="던전 필수품, 포션을 판매한다라!", color=0xe91e63)
    for n, i_info in POTION_SHOP.items(): embed.add_field(name=n, value=f"가격: {i_info['price']:,}원 | {i_info['desc']}", inline=False)
    v = discord.ui.View(); v.add_item(UniversalShopSelect("포션상점", POTION_SHOP))
    await i.response.send_message(embed=embed, view=v)

@client.tree.command(name="인벤토리", description="자신이 가지고 있는 장비들을 확인할 수 있다라!")
async def inv_cmd(interaction: discord.Interaction):
    uid = str(interaction.user.id); create_user_if_not_exists(uid)
    view = InventoryView(uid)
    for item in view.children:
        if isinstance(item, discord.ui.Select): item.options = view.create_options()
    await interaction.response.send_message(embed=create_inventory_embed(interaction.user, uid, "weapon"), view=view)

async def stats_callback(interaction, uid):
    atk, dfe, hp = calculate_stats(uid)
    data = load_inv()
    user = data[uid]
    
    embed = discord.Embed(title=f"📊 {interaction.user.name}의 능력치", color=0xe74c3c)
    embed.add_field(name="⚔️ 공격력", value=f"**{atk}** `(+{user['added_atk']})`", inline=True)
    embed.add_field(name="🛡️ 방어력", value=f"**{dfe}** `(+{user['added_def']})`", inline=True)
    embed.add_field(name="❤️ 체력", value=f"**{hp}** `(+{user['added_hp']})`", inline=True)
    embed.add_field(name="✨ 보너스 포인트", value=f"**{user['point']} P**", inline=False)
    
    view = StatButton(uid)
    
    # [수정됨] 설정: (버튼이름, 스탯키, 상승량, 버튼색깔)
    # ★★★ 여기서 숫자를 바꾸면 실제 적용 수치도 바뀝니다! ★★★
    settings = [
        ("공격력 +2", "added_atk", 2, discord.ButtonStyle.danger),
        ("방어력 +1", "added_def", 1, discord.ButtonStyle.primary),
        ("체력 +10", "added_hp", 10, discord.ButtonStyle.success)
    ]
    
    for label, key, amount, style in settings:
        btn = discord.ui.Button(label=label, style=style)
        # 버튼 누르면 amount 만큼 오르도록 연결
        btn.callback = lambda i, k=key, a=amount: view.add_s(i, k, a)
        view.add_item(btn)

    if interaction.response.is_done(): 
        await interaction.edit_original_response(embed=embed, view=view)
    else: 
        await interaction.response.send_message(embed=embed, view=view)

@client.tree.command(name="스탯", description="능력치를 보거나 올릴 수 있다라!")
async def stats_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    uid = str(interaction.user.id); create_user_if_not_exists(uid)
    await stats_callback(interaction, uid)

@client.tree.command(name="장비창", description="현재 착용하고 있는 장비를 확인한다라!")
async def equip_cmd(i):
    uid = str(i.user.id); user = create_user_if_not_exists(uid); eq = user["equipped"]
    embed = discord.Embed(title="🎒 현재 장착 장비", color=0x3498db)
    for s, d in {"weapon": "🗡️ 무기", "armor": "🛡️ 갑옷", "artifact": "💍 아티팩트"}.items():
        name = eq.get(s, "없음"); item = ITEMS.get(name)
        stat = f" `(ATK+{item['atk']} DEF+{item['def']} HP+{item['hp']})`" if item else ""
        embed.add_field(name=d, value=f"**{name}**{stat}", inline=False)
    await i.response.send_message(embed=embed)

@client.tree.command(name="레벨", description="현재 레벨과 경험치를 확인합니다라!")
async def level_check(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id); user_data = create_user_if_not_exists(user_id)
    lvl = user_data.get("level", 1); exp = user_data.get("exp", 0); req = required_exp(lvl)
    percent = min(exp / req, 1.0); progress = int(percent * 10)
    bar = "🟦" * progress + "⬜" * (10 - progress)
    embed = discord.Embed(title=f"🎖️ {interaction.user.name} 님의 성장 기록", color=0xffcc00)
    embed.add_field(name=f"현재 레벨: **Lv.{lvl}**", value=f"{bar} **({int(percent * 100)}%)**", inline=False)
    embed.add_field(name="경험치 현황", value=f"**{exp}** / {req} XP", inline=True)
    points = user_data.get("point", 0); footer_text = f"다음 레벨까지 {req - exp} XP 남음!"
    if points > 0: footer_text += f" | 💡 스탯 포인트 {points}개 있음 (/스탯)"
    embed.set_footer(text=footer_text)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="던전", description="초보자 숲 (난이도: 하) 에 입장합니다라!")
async def dungeon_1(interaction: discord.Interaction):
    # --- [추가] 쿨타임 체크 시작 ---
    uid = str(interaction.user.id)
    now = time.time()

    # 기록이 있고, 쿨타임(60초)이 아직 안 지났으면 막기
    if uid in dungeon_last_used and now - dungeon_last_used[uid] < DUNGEON_COOLDOWN:
        remain = int(DUNGEON_COOLDOWN - (now - dungeon_last_used[uid]))
        return await interaction.response.send_message(f"⏳ 던전 입장은 힘들다라... 조금만 쉬어라! ({remain}초 남음)", ephemeral=True)
    
    dungeon_last_used[uid] = now

    user_id = str(interaction.user.id); create_user_if_not_exists(user_id)
    view = DungeonView(interaction, user_id, dungeon_level=1)
    await interaction.response.send_message(embed=discord.Embed(title="초보자 숲 입장", description="슬라임이 튀어나올 것 같다라..."), view=view)
    await view.update_battle()

@client.tree.command(name="던전2", description="잊혀진 광산 (난이도: 중하) 에 입장합니다라!")
async def dungeon_2(interaction: discord.Interaction):
    # --- [추가] 쿨타임 체크 시작 ---
    uid = str(interaction.user.id)
    now = time.time()

    # 기록이 있고, 쿨타임(60초)이 아직 안 지났으면 막기
    if uid in dungeon_last_used and now - dungeon_last_used[uid] < DUNGEON_COOLDOWN:
        remain = int(DUNGEON_COOLDOWN - (now - dungeon_last_used[uid]))
        return await interaction.response.send_message(f"⏳ 던전 입장은 힘들다라... 조금만 쉬어라! ({remain}초 남음)", ephemeral=True)
    
    dungeon_last_used[uid] = now

    user_id = str(interaction.user.id); create_user_if_not_exists(user_id)
    view = DungeonView(interaction, user_id, dungeon_level=2)
    await interaction.response.send_message(embed=discord.Embed(title="잊혀진 광산 입장", description="스산한 기운이 느껴진다라...", color=0xe67e22), view=view)
    await view.update_battle()

@client.tree.command(name="던전3", description="엘프의 숲 (난이도: 중) 에 입장합니다라!")
async def dungeon_3(interaction: discord.Interaction):
    # --- [추가] 쿨타임 체크 시작 ---
    uid = str(interaction.user.id)
    now = time.time()

    # 기록이 있고, 쿨타임(60초)이 아직 안 지났으면 막기
    if uid in dungeon_last_used and now - dungeon_last_used[uid] < DUNGEON_COOLDOWN:
        remain = int(DUNGEON_COOLDOWN - (now - dungeon_last_used[uid]))
        return await interaction.response.send_message(f"⏳ 던전 입장은 힘들다라... 조금만 쉬어라! ({remain}초 남음)", ephemeral=True)
    
    dungeon_last_used[uid] = now

    user_id = str(interaction.user.id); create_user_if_not_exists(user_id)
    view = DungeonView(interaction, user_id, dungeon_level=3)
    await interaction.response.send_message(embed=discord.Embed(title="엘프의 숲", description="인적이 드믄 숲이다...", color=0x000000), view=view)
    await view.update_battle()

@client.tree.command(name="던전4", description="매서운 추위의 설산 (난이도: 중상) 에 입장합니다라!")
async def dungeon_4(interaction: discord.Interaction):
    # --- [추가] 쿨타임 체크 시작 ---
    uid = str(interaction.user.id)
    now = time.time()

    # 기록이 있고, 쿨타임(60초)이 아직 안 지났으면 막기
    if uid in dungeon_last_used and now - dungeon_last_used[uid] < DUNGEON_COOLDOWN:
        remain = int(DUNGEON_COOLDOWN - (now - dungeon_last_used[uid]))
        return await interaction.response.send_message(f"⏳ 던전 입장은 힘들다라... 조금만 쉬어라! ({remain}초 남음)", ephemeral=True)
    
    dungeon_last_used[uid] = now

    user_id = str(interaction.user.id); create_user_if_not_exists(user_id)
    view = DungeonView(interaction, user_id, dungeon_level=3)
    await interaction.response.send_message(embed=discord.Embed(title="매서운 추위의 설산", description="따뜻한 옷을 안입으면 안될거 같다...", color=0x02021A), view=view)
    await view.update_battle()

@client.tree.command(name="광산", description="곡괭이질로 광석을 캐고 돈을 법니다라!")
async def mining_cmd(interaction: discord.Interaction):
    view = MiningView(interaction.user.id)
    await interaction.response.send_message(embed=view.get_embed(), view=view)

@client.tree.command(name="장비강화", description="돈을 써서 장비를 강화합니다라!")
async def enhance_cmd(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    create_user_if_not_exists(uid)
    
    # 카테고리 선택 버튼들을 담을 View 생성
    view = discord.ui.View()
    
    # 버튼을 눌렀을 때 실행될 공통 함수
    async def category_callback(i, cat):
        # 다른 사람이 누르면 무시
        if i.user.id != interaction.user.id: return
        
        # 해당 카테고리(weapon/armor/artifact)의 강화 화면 가져오기
        e_view = EnhanceView(uid, cat)
        
        # 강화할 아이템이 없으면 알림
        if not e_view.options:
            await i.response.send_message("강화할 아이템이 없다라!", ephemeral=True)
        else:
            await i.response.send_message(f"**{cat}** 강화 대장간이다라!", view=e_view, ephemeral=True)

    # 1. 무기 버튼
    btn1 = discord.ui.Button(label="🗡️ 무기", style=discord.ButtonStyle.secondary)
    btn1.callback = lambda i: category_callback(i, "weapon")
    
    # 2. 갑옷 버튼
    btn2 = discord.ui.Button(label="🛡️ 갑옷", style=discord.ButtonStyle.secondary)
    btn2.callback = lambda i: category_callback(i, "armor")
    
    # 3. [추가됨] 아티팩트 버튼
    btn3 = discord.ui.Button(label="💍 아티팩트", style=discord.ButtonStyle.secondary)
    btn3.callback = lambda i: category_callback(i, "artifact")
    
    # 뷰에 버튼들 추가
    view.add_item(btn1)
    view.add_item(btn2)
    view.add_item(btn3)
    
    await interaction.response.send_message("어떤 장비를 강화할 거냐?", view=view)

# ---------------- [추가] 랭킹 시스템 ----------------

@client.tree.command(name="순위", description="전체 유저 중 레벨이 높은 TOP 10을 보여줍니다라!")
async def rank_cmd(interaction: discord.Interaction):
    # 계산할 게 많아서 시간이 좀 걸릴 수 있으니 '생각 중...' 상태로 전환
    await interaction.response.defer()
    
    data = load_inv()
    
    # 1. 랭킹 정렬 (레벨이 높은 순서, 레벨이 같으면 경험치 높은 순서)
    # items()로 (유저ID, 데이터) 쌍을 가져와서 정렬
    sorted_users = sorted(
        data.items(), 
        key=lambda item: (item[1].get('level', 1), item[1].get('exp', 0)), 
        reverse=True
    )
    
    # 2. 상위 10명 자르기
    top_10 = sorted_users[:10]
    
    embed = discord.Embed(title="🏆 명예의 전당 (TOP 10)", description="이 서버의 가장 강력한 모험가들이다라!", color=0xffd700)
    
    rank_text = ""
    first_user = None # 1등 유저 정보를 저장할 변수
    
    for index, (uid, user_data) in enumerate(top_10):
        rank = index + 1
        level = user_data.get('level', 1)
        
        # 3. 유저 이름 가져오기 (디스코드 서버에서 조회)
        try:
            user = await client.fetch_user(int(uid))
            name = user.name
            # 1등이면 나중에 프로필 사진 쓰기 위해 저장
            if rank == 1:
                first_user = user
        except:
            name = "(알 수 없는 유저)"
            
        # 4. 능력치 계산 (기존 함수 활용)
        atk, dfe, hp = calculate_stats(uid)
        
        # 5. 출력 형식 꾸미기
        if rank == 1:
            medal = "🥇"
            # 1등은 글씨를 굵게 하고 강조
            row = f"{medal} **1위 : {name}**\n╚ **Lv.{level}** | ⚔️{atk} 🛡️{dfe} ❤️{hp}\n"
        elif rank == 2:
            medal = "🥈"
            row = f"{medal} 2위 : {name} | Lv.{level} | ⚔️{atk} 🛡️{dfe} ❤️{hp}\n"
        elif rank == 3:
            medal = "🥉"
            row = f"{medal} 3위 : {name} | Lv.{level} | ⚔️{atk} 🛡️{dfe} ❤️{hp}\n"
        else:
            row = f"**{rank}위**: {name} | Lv.{level} | ⚔️{atk} 🛡️{dfe} ❤️{hp}\n"
            
        rank_text += row

    if not rank_text:
        rank_text = "아직 모험가가 아무도 없다라..."

    embed.description = rank_text
    
    # [핵심] 1등 유저의 프로필 사진을 썸네일로 설정
    if first_user:
        embed.set_thumbnail(url=first_user.display_avatar.url)
        embed.set_footer(text=f"현재 1위는 {first_user.name} 님이다라! 대단하다라!")
    
    await interaction.followup.send(embed=embed)

@client.tree.command(name="도움말", description="초보 모험가를 위한 가이드북이다라!")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="📜 모험가 가이드북", description="이 봇을 즐기는 방법이다라!", color=0x00ff00)
    
    embed.add_field(name="💰 돈 벌기", value="`/돈내놔`: 용돈 받기\n`/광산`: 광질 미니게임 (연타 필수!)", inline=False)
    embed.add_field(name="⚔️ 전투 & 성장", value="`/던전`: 몬스터 사냥 (1~3단계)\n`/스탯`: 능력치 찍기\n`/장비강화`: 대장간 이용", inline=False)
    embed.add_field(name="🛒 상점 & 아이템", value="`/무기상점`, `/방어구상점`\n`/아티팩트상점`, `/포션상점`\n`/인벤토리`: 내 가방 확인", inline=False)
    embed.add_field(name="🏆 기타", value="`/순위`: 랭킹 확인\n`/장비창`: 내 스펙 확인", inline=False)
    
    embed.set_footer(text="자, 이제 모험을 떠나볼까?")
    await interaction.response.send_message(embed=embed)

# ---------------- [추가] 문의/제보 시스템 ----------------

@client.tree.command(name="문의", description="운영자에게 버그를 제보하거나 건의사항을 보냅니다.")
@app_commands.describe(content="운영자에게 보낼 내용을 적어라!")
async def inquiry_cmd(interaction: discord.Interaction, content: str):
    # 관리자용 채널 ID (본인 채널 ID로 수정하세요라)
    LOG_CHANNEL_ID = 1471454391167881296
    
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    
    if log_channel is None:
        # 이 에러 메시지도 본인만 보이게 설정했습니다라
        return await interaction.response.send_message("문의 채널을 찾을 수 없다라!", ephemeral=True)

    # [핵심] ephemeral=True 를 넣으면 명령어를 친 유저 본인에게만 메시지가 보입니다라!
    await interaction.response.send_message("✅ 문의가 성공적으로 접수되었다라! 나만 볼 수 있는 메시지다라.", ephemeral=True)
    
    # 관리자 채널로 보내는 임베드 (이건 관리자만 있는 채널로 전송되니 안심하세요라)
    embed = discord.Embed(title="📩 새로운 문의 도착!", color=0xff5500)
    embed.add_field(name="보낸 사람", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
    embed.add_field(name="내용", value=content, inline=False)
    embed.add_field(name="보낸 곳", value=f"{interaction.guild.name} / {interaction.channel.name}", inline=False)
    embed.set_footer(text=f"접수 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    await log_channel.send(embed=embed)

@client.tree.command(name="후원", description="로라 RPG의 발전을 위해 따뜻한 마음을 나누어 주세요라!")
async def support_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="💖 로라 RPG 후원 안내", color=0xff69b4)
    embed.description = "후원금은 서버 유지비(Railway)와 기능 개발에 사용됩니다라!"
    
    embed.add_field(name="🎁 후원 혜택", value="• 전용 칭호 [Sponsor] 부여", inline=False)
    embed.add_field(name="🔗 후원 링크", value="[여기에 후원 사이트 주소를 넣으세요라!]", inline=False)
    
    embed.set_footer(text="항상 로라를 아껴주셔서 감사합니다라! 🦊")
    await interaction.response.send_message(embed=embed)


# ---------------- [추가] 데이터 초기화 명령어 ----------------

@client.tree.command(name="초기화", description="[관리자 전용] 모든 유저의 돈과 아이템을 삭제합니다!")
async def reset_all(interaction: discord.Interaction):
    # ★ 여기에 본인의 디스코드 ID를 숫자로 넣으세요! (안 그러면 아무나 초기화 가능)
    MY_ID = 743833695080808578
    
    if interaction.user.id != MY_ID:
        return await interaction.response.send_message("너는 관리자가 아니다라! 썩 물러가라!", ephemeral=True)

    # 1. 빈 데이터({})로 덮어쓰기
    save_data({}) # 돈 초기화
    save_inv({})  # 인벤토리 초기화
    
    # 2. 메모리에 있는 쿨타임 기록도 삭제
    if 'dungeon_last_used' in globals():
        dungeon_last_used.clear()
    
    embed = discord.Embed(title="💣 데이터 초기화 완료", description="모든 유저의 돈과 아이템이 삭제되었다라...\n이제 새로운 세상이다라!", color=0xff0000)
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
