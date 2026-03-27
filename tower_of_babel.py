#!/usr/bin/env python3
"""
バベルの塔シミュレーション (Tower of Babel Simulation)
聖書の創世記11章に基づく高品質なシミュレーション
"""

import random
import time
import sys
import textwrap
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# ANSI カラーコード
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


# 言語定義（古代近東の実際の言語に基づく）
LANGUAGES: Dict[str, Dict[str, str]] = {
    "原始語": {
        "hello":   "šalōm",
        "brick":   "libittu",
        "mortar":  "ḥēmār",
        "build":   "banû",
        "higher":  "elû",
        "together":"yaḥad",
        "name":    "šumu",
        "heaven":  "šamāyim",
        "work":    "milāku",
        "stop":    "šabātu",
    },
    "シュメール語": {
        "hello":   "silim",
        "brick":   "sig4",
        "mortar":  "im",
        "build":   "du",
        "higher":  "an-ta",
        "together":"da",
        "name":    "mu",
        "heaven":  "an",
        "work":    "ak",
        "stop":    "gam",
    },
    "アッカド語": {
        "hello":   "sulmu",
        "brick":   "libittu",
        "mortar":  "ṭiṭṭu",
        "build":   "banû",
        "higher":  "elû",
        "together":"itti",
        "name":    "šumu",
        "heaven":  "šamû",
        "work":    "epēšu",
        "stop":    "kabātu",
    },
    "エラム語": {
        "hello":   "peš",
        "brick":   "kuk",
        "mortar":  "pi",
        "build":   "ak",
        "higher":  "hal",
        "together":"pal",
        "name":    "še",
        "heaven":  "in",
        "work":    "na",
        "stop":    "mar",
    },
    "古ヘブライ語": {
        "hello":   "shalom",
        "brick":   "levena",
        "mortar":  "chemar",
        "build":   "banah",
        "higher":  "alah",
        "together":"yachad",
        "name":    "shem",
        "heaven":  "shamayim",
        "work":    "melachah",
        "stop":    "chadal",
    },
    "フリ語": {
        "hello":   "eia",
        "brick":   "attu",
        "mortar":  "uri",
        "build":   "ašti",
        "higher":  "ardi",
        "together":"mani",
        "name":    "šena",
        "heaven":  "šimigi",
        "work":    "unuv",
        "stop":    "kelu",
    },
}

ORIGINAL_LANG = "原始語"


class WorkerState(Enum):
    WORKING = "作業中"
    CONFUSED = "混乱中"
    IDLE = "待機中"
    FLED = "逃亡"


@dataclass
class Worker:
    name: str
    language: str
    skill: float  # 0.0 – 1.0
    state: WorkerState = WorkerState.WORKING
    bricks_laid: int = 0

    def speak(self, word: str) -> str:
        spoken = LANGUAGES.get(self.language, {}).get(word, word)
        return f"{self.name}[{self.language}]: '{spoken}'"

    def can_communicate(self, other: "Worker") -> bool:
        return self.language == other.language


@dataclass
class TowerLevel:
    level: int
    width: int
    bricks_required: int
    bricks_placed: int = 0
    completed: bool = False

    @property
    def progress(self) -> float:
        if self.bricks_required <= 0:
            return 0.0
        return min(1.0, self.bricks_placed / self.bricks_required)

    def place_brick(self) -> bool:
        """レンガを1個置く。完成したら True を返す。"""
        if self.completed:
            return False
        self.bricks_placed += 1
        if self.bricks_placed >= self.bricks_required:
            self.completed = True
            return True
        return False


class TowerOfBabel:
    def __init__(self, num_workers: int = 20, total_levels: int = 7):
        self.num_workers = num_workers
        self.total_levels = total_levels
        self.workers: List[Worker] = []
        self.levels: List[TowerLevel] = []
        self.current_level_idx: int = 0
        self.language_confused: bool = False
        self.confusion_turn: Optional[int] = None
        self.turn: int = 0

        self._initialize_tower()
        self._initialize_workers()

    # ────────────────────────── 初期化 ──────────────────────────

    def _initialize_tower(self) -> None:
        for i in range(self.total_levels):
            width = self.total_levels - i + 2          # 下層ほど広い
            bricks = width * width
            self.levels.append(TowerLevel(
                level=i + 1,
                width=width,
                bricks_required=bricks,
            ))

    def _initialize_workers(self) -> None:
        names = [
            "ニムロデ", "エノク", "アシュル", "アルパクサデ",
            "カイナン", "シェラ", "エベル", "ペレク",
            "レウ", "セルグ", "ナホル", "テラ",
            "ハラン", "ロト", "イシュカ", "ミルカ",
            "ヨクタン", "シェバ", "ハビラ", "サブタ",
        ]
        for i in range(self.num_workers):
            base = names[i % len(names)]
            name = base if i < len(names) else f"{base}{i // len(names) + 1}"
            self.workers.append(Worker(
                name=name,
                language=ORIGINAL_LANG,
                skill=random.uniform(0.6, 1.0),
            ))

    # ────────────────────────── 表示 ──────────────────────────

    def _display_tower(self) -> None:
        print(f"\n{Color.YELLOW}{'='*62}{Color.RESET}")
        print(f"{Color.BOLD}{Color.YELLOW}  バベルの塔  ─  第{self.turn}ターン{Color.RESET}")
        print(f"{Color.YELLOW}{'='*62}{Color.RESET}")

        max_w = self.total_levels + 4          # 最下層の幅に合わせた余白基準
        completed = [lv for lv in self.levels if lv.completed]
        current = (self.levels[self.current_level_idx]
                   if self.current_level_idx < len(self.levels) else None)

        # 未着工の上層部 ─ 中央の柱だけ表示
        empty_rows = self.total_levels - len(completed) - (
            1 if (current and not current.completed) else 0
        )
        for _ in range(max(0, empty_rows)):
            pad = (max_w) // 2
            print(" " * (pad + 2) + "|")

        # 建設中の階層
        if current and not current.completed:
            w = current.width
            pad = (max_w - w) // 2
            filled = int(w * current.progress)
            bar = "#" * filled + "." * (w - filled)
            print(f"  {' ' * pad}{Color.CYAN}[{bar}]{Color.RESET}"
                  f"  ← 第{current.level}層 ({current.progress * 100:.0f}%)")

        # 完成済み階層（上から下の順に reversed で表示）
        for lv in reversed(completed):
            w = lv.width
            pad = (max_w - w) // 2
            print(f"  {' ' * pad}{Color.GREEN}[{'█' * w}]{Color.RESET}"
                  f"  ← 第{lv.level}層 ✓")

        # 基礎・地面
        print(f"  {Color.YELLOW}{'▓' * (max_w + 2)}{Color.RESET}")
        print(f"  {'─ 地面 ─':^{max_w + 2}}")

        # 統計行
        working  = sum(1 for w in self.workers if w.state == WorkerState.WORKING)
        confused = sum(1 for w in self.workers if w.state == WorkerState.CONFUSED)
        fled     = sum(1 for w in self.workers if w.state == WorkerState.FLED)
        total_b  = sum(w.bricks_laid for w in self.workers)

        print(f"\n  作業中: {Color.GREEN}{working}人{Color.RESET}  "
              f"混乱中: {Color.RED}{confused}人{Color.RESET}  "
              f"逃亡: {Color.MAGENTA}{fled}人{Color.RESET}  "
              f"累積レンガ: {Color.CYAN}{total_b}個{Color.RESET}")

    # ────────────────────────── ゲームロジック ──────────────────────────

    def _confuse_languages(self) -> None:
        """神による言語の混乱（創世記 11:7）"""
        self.language_confused = True
        self.confusion_turn = self.turn

        print(f"\n{Color.BOLD}{Color.RED}{'!' * 62}{Color.RESET}")
        print(f"{Color.BOLD}{Color.RED}  ★ 神による言語の混乱 ★{Color.RESET}")
        print(f"{Color.RED}  「さあ、我々は下って、彼らの言葉を乱し、")
        print(f"   互いに相手の言葉が分からないようにしよう。」")
        print(f"  ── 創世記 11:7{Color.RESET}")
        print(f"{Color.BOLD}{Color.RED}{'!' * 62}{Color.RESET}\n")

        lang_pool = [k for k in LANGUAGES if k != ORIGINAL_LANG]
        for worker in self.workers:
            worker.language = random.choice(lang_pool)
            worker.state = WorkerState.CONFUSED

        print(f"{Color.YELLOW}【混乱の叫び声】{Color.RESET}")
        for w in random.sample(self.workers, min(6, len(self.workers))):
            print(f"  {w.speak('heaven')}  ← 誰も理解できない！")

    def _simulate_turn(self) -> bool:
        """1ターン進める。継続なら True を返す。"""
        self.turn += 1

        if self.current_level_idx >= len(self.levels):
            return False

        current_level = self.levels[self.current_level_idx]

        # ── 混乱後の状態遷移 ──
        if self.language_confused:
            for worker in self.workers:
                if worker.state == WorkerState.CONFUSED:
                    roll = random.random()
                    if roll < 0.25:
                        # 同言語の仲間を見つけて部分回復
                        allies = [w for w in self.workers
                                  if w.language == worker.language and w != worker]
                        if allies:
                            worker.state = WorkerState.WORKING
                            worker.skill *= 0.65    # 効率低下
                    elif roll < 0.45:
                        worker.state = WorkerState.FLED

        # ── 作業フェーズ ──
        active = [w for w in self.workers if w.state == WorkerState.WORKING]

        for worker in active:
            efficiency = worker.skill
            if self.language_confused:
                group_size = sum(
                    1 for w in active if w.language == worker.language
                )
                if group_size < 3:
                    efficiency *= 0.35   # 孤立グループは大幅効率低下

            if random.random() < efficiency:
                just_completed = current_level.place_brick()
                worker.bricks_laid += 1
                if just_completed:
                    print(f"\n{Color.GREEN}  ★ 第{current_level.level}層が完成！{Color.RESET}")
                    self.current_level_idx += 1
                    break   # 次の層へ

        return True

    def _check_confusion_trigger(self) -> bool:
        """塔が半分を超えたら言語混乱を発動"""
        if self.language_confused:
            return False
        completed = sum(1 for lv in self.levels if lv.completed)
        return completed >= 3

    # ────────────────────────── メインループ ──────────────────────────

    def run(self, max_turns: int = 80) -> None:
        # ─ タイトル ─
        print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 62}{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}  バベルの塔  ─  文明の野望と神の摂理{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}  Tower of Babel Simulation  (Genesis 11:1-9){Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}{'=' * 62}{Color.RESET}")
        print(f"\n  ワーカー数: {self.num_workers}人 │ 目標層数: {self.total_levels}層\n")

        # ─ 物語の始まり ─
        print(f"{Color.YELLOW}【物語の始まり】{Color.RESET}")
        print(textwrap.fill(
            "「全地は一つの言葉を話し、同じことばを使っていた。」"
            "人々は東の方から移動し、シンアルの地の平野を見つけてそこに住んだ。"
            "彼らは言い合った。「さあ、レンガを作って、よく焼こう。」"
            "石の代わりにレンガを用い、漆喰の代わりにアスファルトを用いた。",
            width=62, initial_indent="  ", subsequent_indent="  "
        ))
        print(f"  ── 創世記 11:1-3\n")

        # ─ 建設宣言 ─
        leader = self.workers[0]
        print(f"{Color.CYAN}【リーダーの宣言】{Color.RESET}")
        print(f"  {leader.speak('build')}")
        print(f"  {leader.speak('heaven')}")
        print(f"  {leader.speak('together')}\n")

        # ─ メインループ ─
        for _ in range(max_turns):
            if self._check_confusion_trigger():
                self._confuse_languages()

            if not self._simulate_turn():
                break

            # 数ターンごとに塔を描画
            if self.turn % 6 == 0:
                self._display_tower()

            # 全員が作業不能になったら終了
            still_active = sum(
                1 for w in self.workers
                if w.state in (WorkerState.WORKING, WorkerState.CONFUSED)
            )
            if still_active == 0:
                print(f"\n{Color.RED}  全ワーカーが逃散しました。建設は中断されました。{Color.RESET}")
                break

            # 全層完成
            if self.current_level_idx >= self.total_levels:
                print(f"\n{Color.YELLOW}  ⚠ 塔が天に届こうとしています！{Color.RESET}")
                break

        # ─ 最終描画 ─
        self._display_tower()
        self._show_final_report()

    def _show_final_report(self) -> None:
        print(f"\n{Color.BOLD}{'=' * 62}{Color.RESET}")
        print(f"{Color.BOLD}  最終レポート{Color.RESET}")
        print(f"{'=' * 62}")

        completed = sum(1 for lv in self.levels if lv.completed)
        total_b = sum(w.bricks_laid for w in self.workers)

        print(f"  完成した層数  : {completed} / {self.total_levels}")
        print(f"  経過ターン数  : {self.turn}")
        print(f"  総レンガ数    : {total_b:,}個")

        if self.language_confused and self.confusion_turn is not None:
            print(f"\n  言語混乱発生  : 第{self.confusion_turn}ターン")
            groups: Dict[str, int] = {}
            for w in self.workers:
                groups[w.language] = groups.get(w.language, 0) + 1
            print(f"  分散言語グループ数: {len(groups)}")
            for lang, cnt in sorted(groups.items(), key=lambda x: -x[1]):
                print(f"    {lang}: {cnt}人")

        print(f"\n  【ワーカー最終状態】")
        for state in WorkerState:
            cnt = sum(1 for w in self.workers if w.state == state)
            if cnt:
                print(f"    {state.value}: {cnt}人")

        # 締めくくりの聖書の言葉
        print(f"\n{Color.YELLOW}【聖書の言葉】{Color.RESET}")
        print(textwrap.fill(
            "「こうして主は人々を、そこから全地に散らされた。"
            "彼らはその都市の建設をやめた。"
            "それゆえその地の名はバベルと呼ばれた。"
            "主がそこで全地の言語を乱し、そこから主が全地に人々を散らされたからである。」",
            width=62, initial_indent="  ", subsequent_indent="  "
        ))
        print(f"  ── 創世記 11:8-9\n")


def main() -> None:
    random.seed(42)
    try:
        sim = TowerOfBabel(num_workers=20, total_levels=7)
        sim.run(max_turns=120)
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}シミュレーションが中断されました。{Color.RESET}")


if __name__ == "__main__":
    main()
