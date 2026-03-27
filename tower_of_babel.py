#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
バベルの塔シミュレーション (Tower of Babel Simulation)
聖書の創世記11章に基づく高品質なシミュレーション
Windows / Mac / Linux どこでも動作するよう UTF-8 エンコード対応済み
"""

import random
import time
import sys
import os
import textwrap
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


# ─────────────────────── エンコード設定（最初に実行） ───────────────────────

def _setup_encoding() -> None:
    """Windows 等で UTF-8 出力を強制し、エンコードエラーで落ちないようにする。"""
    if sys.platform == "win32":
        try:
            os.system("chcp 65001 > nul 2>&1")
        except Exception:
            pass
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
            except Exception:
                pass


_setup_encoding()

# ─────────────────────── ANSI カラー（非対応端末は無効化） ───────────────────

def _ansi_supported() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes
            k = ctypes.windll.kernel32  # type: ignore[attr-defined]
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_USE_COLOR = _ansi_supported()


class Color:
    RED     = '\033[91m' if _USE_COLOR else ''
    GREEN   = '\033[92m' if _USE_COLOR else ''
    YELLOW  = '\033[93m' if _USE_COLOR else ''
    BLUE    = '\033[94m' if _USE_COLOR else ''
    MAGENTA = '\033[95m' if _USE_COLOR else ''
    CYAN    = '\033[96m' if _USE_COLOR else ''
    WHITE   = '\033[97m' if _USE_COLOR else ''
    BOLD    = '\033[1m'  if _USE_COLOR else ''
    RESET   = '\033[0m'  if _USE_COLOR else ''


# ─────────────────────── 安全な print ───────────────────────────────────────

_STDOUT_ENC: str = getattr(sys.stdout, "encoding", None) or "utf-8"


def _p(*args: object, sep: str = " ", end: str = "\n") -> None:
    """エンコード不可な文字を '?' に置換して出力クラッシュを防ぐ。"""
    text = sep.join(str(a) for a in args)
    safe = text.encode(_STDOUT_ENC, errors="replace").decode(_STDOUT_ENC)
    sys.stdout.write(safe + end)
    sys.stdout.flush()


# ─────────────────────── 言語定義 ────────────────────────────────────────────

LANGUAGES: Dict[str, Dict[str, str]] = {
    "原始語": {
        "hello":    "šalōm",
        "brick":    "libittu",
        "mortar":   "ḥēmār",
        "build":    "banû",
        "higher":   "elû",
        "together": "yaḥad",
        "name":     "šumu",
        "heaven":   "šamāyim",
        "work":     "milāku",
        "stop":     "šabātu",
    },
    "シュメール語": {
        "hello":    "silim",
        "brick":    "sig4",
        "mortar":   "im",
        "build":    "du",
        "higher":   "an-ta",
        "together": "da",
        "name":     "mu",
        "heaven":   "an",
        "work":     "ak",
        "stop":     "gam",
    },
    "アッカド語": {
        "hello":    "sulmu",
        "brick":    "libittu",
        "mortar":   "tittu",
        "build":    "banu",
        "higher":   "elu",
        "together": "itti",
        "name":     "shumu",
        "heaven":   "shamu",
        "work":     "epeshu",
        "stop":     "kabatu",
    },
    "エラム語": {
        "hello":    "pesh",
        "brick":    "kuk",
        "mortar":   "pi",
        "build":    "ak",
        "higher":   "hal",
        "together": "pal",
        "name":     "she",
        "heaven":   "in",
        "work":     "na",
        "stop":     "mar",
    },
    "古ヘブライ語": {
        "hello":    "shalom",
        "brick":    "levena",
        "mortar":   "chemar",
        "build":    "banah",
        "higher":   "alah",
        "together": "yachad",
        "name":     "shem",
        "heaven":   "shamayim",
        "work":     "melachah",
        "stop":     "chadal",
    },
    "フリ語": {
        "hello":    "eia",
        "brick":    "attu",
        "mortar":   "uri",
        "build":    "ashti",
        "higher":   "ardi",
        "together": "mani",
        "name":     "shena",
        "heaven":   "shimigi",
        "work":     "unuv",
        "stop":     "kelu",
    },
}

ORIGINAL_LANG = "原始語"


# ─────────────────────── データクラス ────────────────────────────────────────

class WorkerState(Enum):
    WORKING = "作業中"
    CONFUSED = "混乱中"
    IDLE = "待機中"
    FLED = "逃亡"


@dataclass
class Worker:
    name: str
    language: str
    skill: float        # 0.0 – 1.0
    state: WorkerState = WorkerState.WORKING
    bricks_laid: int = 0

    def speak(self, word: str) -> str:
        spoken = LANGUAGES.get(self.language, {}).get(word, word)
        enc = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
        spoken_safe = spoken.encode(enc, errors="replace").decode(enc)
        return f"{self.name}[{self.language}]: '{spoken_safe}'"

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


# ─────────────────────── メインクラス ────────────────────────────────────────

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

    # ── 初期化 ────────────────────────────────────────────────────────────────

    def _initialize_tower(self) -> None:
        for i in range(self.total_levels):
            width = self.total_levels - i + 2      # 下層ほど広い
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

    # ── 表示 ──────────────────────────────────────────────────────────────────

    def _display_tower(self) -> None:
        _p(f"\n{Color.YELLOW}{'=' * 62}{Color.RESET}")
        _p(f"{Color.BOLD}{Color.YELLOW}  バベルの塔  ─  第{self.turn}ターン{Color.RESET}")
        _p(f"{Color.YELLOW}{'=' * 62}{Color.RESET}")

        max_w = self.total_levels + 4
        completed = [lv for lv in self.levels if lv.completed]
        current = (self.levels[self.current_level_idx]
                   if self.current_level_idx < len(self.levels) else None)

        # 未着工の上層部 ─ 中央の柱
        empty_rows = self.total_levels - len(completed) - (
            1 if (current and not current.completed) else 0
        )
        for _ in range(max(0, empty_rows)):
            pad = max_w // 2
            _p(" " * (pad + 2) + "|")

        # 建設中の階層
        if current and not current.completed:
            w = current.width
            pad = (max_w - w) // 2
            filled = int(w * current.progress)
            bar = "#" * filled + "." * (w - filled)
            _p(f"  {' ' * pad}{Color.CYAN}[{bar}]{Color.RESET}"
               f"  <- 第{current.level}層 ({current.progress * 100:.0f}%)")

        # 完成済み階層
        for lv in reversed(completed):
            w = lv.width
            pad = (max_w - w) // 2
            _p(f"  {' ' * pad}{Color.GREEN}[{'#' * w}]{Color.RESET}"
               f"  <- 第{lv.level}層 完成")

        # 基礎・地面
        _p(f"  {Color.YELLOW}{'=' * (max_w + 2)}{Color.RESET}")
        _p(f"  {'-- 地面 --':^{max_w + 2}}")

        # 統計
        working  = sum(1 for w in self.workers if w.state == WorkerState.WORKING)
        confused = sum(1 for w in self.workers if w.state == WorkerState.CONFUSED)
        fled     = sum(1 for w in self.workers if w.state == WorkerState.FLED)
        total_b  = sum(w.bricks_laid for w in self.workers)

        _p(f"\n  作業中: {Color.GREEN}{working}人{Color.RESET}  "
           f"混乱中: {Color.RED}{confused}人{Color.RESET}  "
           f"逃亡: {Color.MAGENTA}{fled}人{Color.RESET}  "
           f"累積レンガ: {Color.CYAN}{total_b}個{Color.RESET}")

    # ── ゲームロジック ────────────────────────────────────────────────────────

    def _confuse_languages(self) -> None:
        """神による言語の混乱（創世記 11:7）"""
        self.language_confused = True
        self.confusion_turn = self.turn

        _p(f"\n{Color.BOLD}{Color.RED}{'!' * 62}{Color.RESET}")
        _p(f"{Color.BOLD}{Color.RED}  ★ 神による言語の混乱 ★{Color.RESET}")
        _p(f"{Color.RED}  「さあ、我々は下って、彼らの言葉を乱し、")
        _p(f"   互いに相手の言葉が分からないようにしよう。」")
        _p(f"  ── 創世記 11:7{Color.RESET}")
        _p(f"{Color.BOLD}{Color.RED}{'!' * 62}{Color.RESET}\n")

        lang_pool = [k for k in LANGUAGES if k != ORIGINAL_LANG]
        for worker in self.workers:
            worker.language = random.choice(lang_pool)
            worker.state = WorkerState.CONFUSED

        _p(f"{Color.YELLOW}【混乱の叫び声】{Color.RESET}")
        for w in random.sample(self.workers, min(6, len(self.workers))):
            _p(f"  {w.speak('heaven')}  <- 誰も理解できない！")

    def _simulate_turn(self) -> bool:
        """1ターン進める。継続なら True を返す。"""
        self.turn += 1

        if self.current_level_idx >= len(self.levels):
            return False

        current_level = self.levels[self.current_level_idx]

        # 混乱後の状態遷移
        if self.language_confused:
            for worker in self.workers:
                if worker.state == WorkerState.CONFUSED:
                    roll = random.random()
                    if roll < 0.25:
                        allies = [w for w in self.workers
                                  if w.language == worker.language and w != worker]
                        if allies:
                            worker.state = WorkerState.WORKING
                            worker.skill *= 0.65
                    elif roll < 0.45:
                        worker.state = WorkerState.FLED

        # 作業フェーズ
        active = [w for w in self.workers if w.state == WorkerState.WORKING]

        for worker in active:
            efficiency = worker.skill
            if self.language_confused:
                group_size = sum(1 for w in active if w.language == worker.language)
                if group_size < 3:
                    efficiency *= 0.35

            if random.random() < efficiency:
                just_completed = current_level.place_brick()
                worker.bricks_laid += 1
                if just_completed:
                    _p(f"\n{Color.GREEN}  ★ 第{current_level.level}層が完成！{Color.RESET}")
                    self.current_level_idx += 1
                    break

        return True

    def _check_confusion_trigger(self) -> bool:
        if self.language_confused:
            return False
        completed = sum(1 for lv in self.levels if lv.completed)
        return completed >= 3

    # ── メインループ ──────────────────────────────────────────────────────────

    def run(self, max_turns: int = 120) -> None:
        _p(f"\n{Color.BOLD}{Color.CYAN}{'=' * 62}{Color.RESET}")
        _p(f"{Color.BOLD}{Color.CYAN}  バベルの塔  ─  文明の野望と神の摂理{Color.RESET}")
        _p(f"{Color.BOLD}{Color.CYAN}  Tower of Babel Simulation  (Genesis 11:1-9){Color.RESET}")
        _p(f"{Color.BOLD}{Color.CYAN}{'=' * 62}{Color.RESET}")
        _p(f"\n  ワーカー数: {self.num_workers}人  目標層数: {self.total_levels}層\n")

        _p(f"{Color.YELLOW}【物語の始まり】{Color.RESET}")
        _p(textwrap.fill(
            "「全地は一つの言葉を話し、同じことばを使っていた。」"
            "人々は東の方から移動し、シンアルの地の平野を見つけてそこに住んだ。"
            "彼らは言い合った。「さあ、レンガを作って、よく焼こう。」"
            "石の代わりにレンガを用い、漆喰の代わりにアスファルトを用いた。",
            width=62, initial_indent="  ", subsequent_indent="  "
        ))
        _p(f"  ── 創世記 11:1-3\n")

        leader = self.workers[0]
        _p(f"{Color.CYAN}【リーダーの宣言】{Color.RESET}")
        _p(f"  {leader.speak('build')}")
        _p(f"  {leader.speak('heaven')}")
        _p(f"  {leader.speak('together')}\n")

        for _ in range(max_turns):
            if self._check_confusion_trigger():
                self._confuse_languages()

            if not self._simulate_turn():
                break

            if self.turn % 6 == 0:
                self._display_tower()

            still_active = sum(
                1 for w in self.workers
                if w.state in (WorkerState.WORKING, WorkerState.CONFUSED)
            )
            if still_active == 0:
                _p(f"\n{Color.RED}  全ワーカーが逃散しました。建設は中断されました。{Color.RESET}")
                break

            if self.current_level_idx >= self.total_levels:
                _p(f"\n{Color.YELLOW}  塔が天に届こうとしています！{Color.RESET}")
                break

        self._display_tower()
        self._show_final_report()

    def _show_final_report(self) -> None:
        _p(f"\n{Color.BOLD}{'=' * 62}{Color.RESET}")
        _p(f"{Color.BOLD}  最終レポート{Color.RESET}")
        _p(f"{'=' * 62}")

        completed = sum(1 for lv in self.levels if lv.completed)
        total_b = sum(w.bricks_laid for w in self.workers)

        _p(f"  完成した層数  : {completed} / {self.total_levels}")
        _p(f"  経過ターン数  : {self.turn}")
        _p(f"  総レンガ数    : {total_b:,}個")

        if self.language_confused and self.confusion_turn is not None:
            _p(f"\n  言語混乱発生  : 第{self.confusion_turn}ターン")
            groups: Dict[str, int] = {}
            for w in self.workers:
                groups[w.language] = groups.get(w.language, 0) + 1
            _p(f"  分散言語グループ数: {len(groups)}")
            for lang, cnt in sorted(groups.items(), key=lambda x: -x[1]):
                _p(f"    {lang}: {cnt}人")

        _p(f"\n  【ワーカー最終状態】")
        for state in WorkerState:
            cnt = sum(1 for w in self.workers if w.state == state)
            if cnt:
                _p(f"    {state.value}: {cnt}人")

        _p(f"\n{Color.YELLOW}【聖書の言葉】{Color.RESET}")
        _p(textwrap.fill(
            "「こうして主は人々を、そこから全地に散らされた。"
            "彼らはその都市の建設をやめた。"
            "それゆえその地の名はバベルと呼ばれた。"
            "主がそこで全地の言語を乱し、そこから主が全地に人々を散らされたからである。」",
            width=62, initial_indent="  ", subsequent_indent="  "
        ))
        _p(f"  ── 創世記 11:8-9\n")


# ─────────────────────── エントリーポイント ─────────────────────────────────

def main() -> None:
    # Python バージョン確認（3.7以上が必要）
    if sys.version_info < (3, 7):
        sys.stderr.write(
            "エラー: Python 3.7以上が必要です。\n"
            f"現在のバージョン: {sys.version}\n"
        )
        input("Enterキーで終了...")
        sys.exit(1)

    random.seed(42)
    try:
        sim = TowerOfBabel(num_workers=20, total_levels=7)
        sim.run(max_turns=120)
    except KeyboardInterrupt:
        _p(f"\n\n{Color.YELLOW}シミュレーションが中断されました。{Color.RESET}")
    except Exception as e:
        # クラッシュ時にエラー内容を表示してウィンドウを閉じないようにする
        import traceback
        _p("\n" + "=" * 62)
        _p("エラーが発生しました:")
        _p(traceback.format_exc())
        _p("=" * 62)
    finally:
        # Windows でダブルクリック実行した際にウィンドウがすぐ閉じないよう待機
        if sys.platform == "win32":
            input("\nEnterキーを押して終了...")


if __name__ == "__main__":
    main()
