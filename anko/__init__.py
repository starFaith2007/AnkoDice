from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
import random
import re
from .config import Config
from nonebot import require
from nonebot.adapters import Message, Event
import nonebot_plugin_localstore as store
import csv
from nonebot.exception import FinishedException


__plugin_meta__ = PluginMetadata(
    name="anko",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
# 定义部分

name = on_command(
    "bot",
    rule=to_me(),
    aliases={"介绍", "介绍你自己", "介绍自己", "你是谁", "你是谁？"},
    priority=10,
    block=True,
)
r_cmd = on_command("r", priority=3, block=True)
r_get = on_command("rget", priority=2, block=True)
anka = on_command("anka", priority=3, block=True)
ankain = on_command("akin", priority=3, block=True)
ankaget = on_command("akget", priority=3, block=True)


# 实现部分
# 1.自我介绍
@name.handle()
async def handle_function():
    await name.finish("我是安科专用骰娘「西园寺世界」。\n可用指令如下：\n1.骰点：/r\n2.查询骰点记录：/rget\n3.安价创建、抽取：/anka\n4.添加安价选项：/akin\n5.查看、删除安价：/akget \n6.今日人品：/jrrp\n^_^请对我一心一意吧^_^")


# 2.骰子基本功能
# @r_cmd.handle()
# async def r_cmd_function(args: Message = CommandArg()):
#     dices = args.extract_plain_text()
#     rmlist = []
#     if re.fullmatch(r'\d+', dices):
#         # 将单个数字转换为"1dN"的形式
#         dice_sides = int(dices)
#         if dice_sides <= 0:
#             await r_cmd.finish()
#         rm = random.randint(1, dice_sides)
#         await r_cmd.finish(f"{dices}={rm}")
#     dice_pattern = r'\d*d\d+'
#     dice_matchs = list(re.finditer(dice_pattern, dices, re.IGNORECASE))
#     if not dice_matchs:
#         try:
#             rm = eval(dices)
#             await r_cmd.finish(f"{dices}={rm}")
#         except:
#             await r_cmd.finish()
#     dice_results = []
#     for match in dice_matchs:
#         dice_expr = match.group(0)
#         dice_parts = dice_expr.lower().split('d')
#         num_dice_str = dice_parts[0]
#         dice_sides = int(dice_parts[1])
#         num_dice = int(num_dice_str) if num_dice_str else 1
#         dice_result = 0
#         for _ in range(num_dice):
#             dice_result += random.randint(1, dice_sides)
#             rmlist.append(dice_result)
#         dice_results.append((match.start(), match.end(), dice_result))
#     dice_results.sort(reverse=True)
#     result_expr = dices
#     for start, end, result in dice_results:
#         result_expr = result_expr[:start] + str(result) + result_expr[end:]
#     try:
#         rm = eval(result_expr)
#         if result_expr.isdigit():
#             await r_cmd.finish(f"{dices}={rm}")
#         else:
#             await r_cmd.finish(f"{dices}={result_expr}={rm}")
#     except:
#         await r_cmd.finish()
@r_cmd.handle()
async def r_cmd_function(event: Event, args: Message = CommandArg()):
    full_text = args.extract_plain_text().strip()

    # 分离骰子表达式和原因文字
    dice_expr = full_text
    reason = ""

    # 1. 首先处理/rd和/rd原因格式（必须以d开头）
    if full_text.lower().startswith("d"):
        # /rd原因 或 /rd 原因 格式
        if len(full_text) == 1:  # 只有一个"d"
            dice_expr = "1d100"
            reason = ""
        else:
            # 移除开头的d，剩余部分作为原因
            reason = full_text[1:].strip()
            dice_expr = "1d100"
    else:
        # 2. 匹配其他格式中的文字部分
        # 先尝试匹配带空格的格式: /r 1d6 我的原因
        space_match = re.match(
            r"^([\ddD\+\-\*\/\(\)\.\s]+)\s+(.*)$", full_text, re.IGNORECASE
        )
        if space_match:
            dice_expr = space_match.group(1).strip()
            reason = space_match.group(2).strip()
        else:
            # 3. /r1d6我的原因 格式（无空格）
            # 提取出骰子表达式，剩余部分作为原因
            dice_pattern = r"^([\d\(][\ddD\+\-\*\/\(\)\.]*)(.*)$"
            dice_match = re.match(dice_pattern, full_text, re.IGNORECASE)
            if dice_match:
                dice_expr = dice_match.group(1).strip()
                reason = dice_match.group(2).strip()

    # 清理骰子表达式中的空格
    dice_expr_clean = dice_expr.replace(" ", "")

    # 检查是否只输入一个数字（直接骰点）
    if re.fullmatch(r"\d+", dice_expr_clean):
        # 将单个数字转换为"1dN"的形式
        dice_sides = int(dice_expr_clean)
        if dice_sides <= 0:
            await r_cmd.finish()
        rm = random.randint(1, dice_sides)
        result_text = f"{dice_expr}={rm}"
        if reason:
            result_text += f" ({reason})"
        user_id: str = event.get_user_id()
        try:
            userdata = store.get_plugin_data_file(f"{user_id}.txt")
            with userdata.open("a", encoding="utf-8") as f:
                f.write(f"{result_text}\n")
        except Exception as e:
            pass
        await r_cmd.finish(result_text)

    # 查找所有骰子表达式
    dice_pattern = r"\d*d\d+"
    dice_matchs = list(re.finditer(dice_pattern, dice_expr_clean, re.IGNORECASE))

    # 如果没有骰子表达式，尝试计算算术表达式
    if not dice_matchs:
        try:
            rm = eval(dice_expr_clean)
            result_text = f"{dice_expr}={rm}"
            if reason:
                result_text += f" ({reason})"
                user_id: str = event.get_user_id()
            try:
                userdata = store.get_plugin_data_file(f"{user_id}.txt")
                with userdata.open("a", encoding="utf-8") as f:
                    f.write(f"{result_text}\n")
            except Exception as e:
                pass
            await r_cmd.finish(result_text)
        except:
            await r_cmd.finish()

    # 计算所有骰子表达式的结果
    dice_results = []
    for match in dice_matchs:
        dice_expr_part = match.group(0)
        dice_parts = dice_expr_part.lower().split("d")
        num_dice_str = dice_parts[0]
        dice_sides = int(dice_parts[1])
        num_dice = int(num_dice_str) if num_dice_str else 1
        dice_result = 0
        for _ in range(num_dice):
            dice_result += random.randint(1, dice_sides)
        dice_results.append((match.start(), match.end(), dice_result))

    dice_results.sort(reverse=True)
    result_expr = dice_expr_clean

    for start, end, result in dice_results:
        result_expr = result_expr[:start] + str(result) + result_expr[end:]

    try:
        rm = eval(result_expr)
        if dice_expr_clean.isdigit():
            result_text = f"{dice_expr}={rm}"
        else:
            result_text = f"{dice_expr}={result_expr}={rm}"

        if reason:
            result_text += f" ({reason})"
            user_id: str = event.get_user_id()
            try:
                userdata = store.get_plugin_data_file(f"{user_id}.txt")
                with userdata.open("a", encoding="utf-8") as f:
                    f.write(f"{result_text}\n")
            except Exception as e:
                pass
            await r_cmd.finish(result_text)
    except:
        await r_cmd.finish()


# @r_get.handle()
# async def r_get_function(event: Event, args: Message = CommandArg())
#     user_id: str = event.get_user_id()
#     userdata = store.get_plugin_data_file(f"{user_id}.txt")
#     with userdata.open("a", encoding="utf-8") as f:
#         f.write(f"{result_text}\n")
@r_get.handle()
async def r_get_function(event: Event, args: Message = CommandArg()):
    user_id: str = event.get_user_id()
    # 获取参数，判断是否指定了要读取的行数
    arg_text = args.extract_plain_text().strip()
    lines_to_read = 30  # 默认读取用户指定数量的骰点记录

    if arg_text.isdigit():
        lines_to_read = int(arg_text)
        # 限制最大读取行数，避免过载
        if lines_to_read > 500:
            lines_to_read = 500
        elif lines_to_read < 1:
            lines_to_read = 1

    try:
        userdata = store.get_plugin_data_file(f"{user_id}.txt")

        # 检查文件是否存在
        if not userdata.exists():
            await r_get.finish(f"用户 {user_id} 还没有任何掷骰记录")

        # 读取文件内容
        with userdata.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        # 获取最后指定行数的记录
        total_lines = len(lines)
        if total_lines == 0:
            await r_get.finish(f"用户 {user_id} 还没有任何掷骰记录")

        # 计算开始行
        start_line = max(0, total_lines - lines_to_read)

        # 获取最后指定行数的记录
        recent_lines = lines[start_line:]

        # 构建回复消息
        if total_lines <= lines_to_read:
            reply_msg = f"用户 {user_id} 的全部记录（共 {total_lines} 条）：\n"
        else:
            reply_msg = (
                f"用户 {user_id} 最近 {lines_to_read} 条记录（共 {total_lines} 条）：\n"
            )

        # 添加行号
        for i, line in enumerate(recent_lines, start=start_line + 1):
            reply_msg += f"{i}. {line.strip()}\n"

        # 如果记录太多，可能需要分割发送（这里假设不超过消息长度限制）
        await r_get.finish(reply_msg)
    except FinishedException:
        raise
    except Exception as e:
        await r_get.finish(f"读取记录失败: {str(e)}")


# @anka.handle()
# async def anka_function(args: Message = CommandArg()):
#     plak = args.extract_plain_text()
#     store.get_plugin_data_file(f"{plak}.txt")
#     await anka.finish("安价已创建")
@anka.handle()
async def anka_function(args: Message = CommandArg()):
    plak = args.extract_plain_text()
    if not plak:
        await anka.finish("请输入安价名称")
        return

    # 检查文件是否存在
    data_file = store.get_plugin_data_file(f"{plak}.txt")

    if not data_file.exists():
        # 文件不存在，创建新安价
        await anka.finish("安价已创建")
    else:
        # 文件已存在，随机抽取一行
        try:
            # 读取文件内容，尝试多种编码
            lines = []
            encodings_to_try = ["utf-8", "gbk", "utf-8-sig", "cp1252"]

            for encoding in encodings_to_try:
                try:
                    with data_file.open("r", encoding=encoding) as f:
                        lines = f.readlines()
                    break  # 如果成功读取，跳出循环
                except UnicodeDecodeError:
                    continue  # 尝试下一种编码

            if not lines:  # 如果所有编码都失败，尝试使用错误忽略模式
                try:
                    with data_file.open("r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    await anka.finish(f"读取安价 “{plak}” 失败：文件编码无法识别")
                    return

            # 获取总行数
            total_lines = len(lines)
            if total_lines == 0:
                await anka.finish(f"安价 “{plak}” 还没有任何内容")
                return

            # 随机选择一行
            random_index = random.randint(0, total_lines - 1)
            selected_line = lines[random_index].strip()

            # 构建回复消息
            reply_msg = f"安价 “{plak}” （共 {total_lines} 条）：\n"
            reply_msg += f"🎲 第 {random_index + 1} 行：{selected_line}"

            await anka.finish(reply_msg)

        except FinishedException:
            raise
        except Exception as e:
            await anka.finish(f"抽取安价失败: {str(e)}")


@ankain.handle()
async def ankain_function(args: Message = CommandArg()):
    plak = args.extract_plain_text()
    parts = plak.split("|")
    if len(parts) == 2:
        ak = parts[0]
        pl = parts[1]
        data_file = store.get_plugin_data_file(f"{ak}.txt")
        with data_file.open("a", encoding="utf-8") as f:
            f.write(f"{pl}\n")
        await ankain.finish("安价已录入")
    else:
        await ankain.finish(
            "格式不匹配，请按照以下格式录入：导游设置的安价名|你的安价内容"
        )


@ankaget.handle()
async def ankaget_function(args: Message = CommandArg()):
    # 获取参数并分割
    arg_text = args.extract_plain_text().strip()
    if not arg_text:
        await ankaget.finish(
            "请输入安价名称，可选的格式：安价名 [行数] 或 安价名 [起始行-结束行] 或 安价名 -行号（删除）"
        )
        return

    # 解析参数：支持三种格式
    # 1. 安价名 -行号 (删除指定行)
    # 2. 安价名 行数 (例如：测试安价 10)
    # 3. 安价名 起始行-结束行 (例如：测试安价 5-15)
    # 4. 只有安价名 (默认显示最后50行)

    parts = arg_text.split()
    if len(parts) == 1:
        # 只有安价名，默认显示最后50行
        ak_name = parts[0]
        lines_to_read = 50
        start_line = None
        end_line = None
        delete_mode = False
        line_to_delete = None
    elif len(parts) == 2:
        ak_name = parts[0]
        param = parts[1]

        # 检查是否是删除模式 (如 -5)
        if param.startswith("-") and param[1:].isdigit():
            # 删除模式
            delete_mode = True
            line_to_delete = int(param[1:])
            lines_to_read = None
            start_line = None
            end_line = None
        elif "-" in param:
            # 检查是否是范围格式 (如 5-15)
            range_parts = param.split("-")
            if (
                len(range_parts) == 2
                and range_parts[0].isdigit()
                and range_parts[1].isdigit()
            ):
                start_line = int(range_parts[0])
                end_line = int(range_parts[1])
                # 确保起始行不大于结束行
                if start_line > end_line:
                    start_line, end_line = end_line, start_line
                lines_to_read = None  # 使用范围模式
                delete_mode = False
            else:
                await ankaget.finish(
                    "范围格式错误，请使用格式：起始行-结束行 (例如：5-15) 或 -行号 (例如：-5 删除第5行)"
                )
                return
        elif param.isdigit():
            # 纯数字，表示要显示的行数
            lines_to_read = int(param)
            start_line = None
            end_line = None
            delete_mode = False

            # 限制最大读取行数
            if lines_to_read > 200:
                lines_to_read = 200
            elif lines_to_read < 1:
                lines_to_read = 1
        else:
            await ankaget.finish(
                "参数格式错误，请使用：安价名 [行数] 或 安价名 [起始行-结束行] 或 安价名 -行号（删除）"
            )
            return
    else:
        await ankaget.finish(
            "参数过多，请使用：安价名 [行数] 或 安价名 [起始行-结束行] 或 安价名 -行号（删除）"
        )
        return

    try:
        data_file = store.get_plugin_data_file(f"{ak_name}.txt")

        # 检查文件是否存在
        if not data_file.exists():
            await ankaget.finish(f"安价 '{ak_name}' 不存在")
            return

        # 读取文件内容，尝试多种编码
        lines = []
        encodings_to_try = ["utf-8", "gbk", "utf-8-sig", "cp1252"]

        for encoding in encodings_to_try:
            try:
                with data_file.open("r", encoding=encoding) as f:
                    lines = f.readlines()
                break  # 如果成功读取，跳出循环
            except UnicodeDecodeError:
                continue  # 尝试下一种编码

        if not lines:  # 如果所有编码都失败，尝试使用错误忽略模式
            try:
                with data_file.open("r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception:
                await ankaget.finish(f"读取安价 '{ak_name}' 失败：文件编码无法识别")
                return

        # 获取总行数
        total_lines = len(lines)

        # 删除模式
        if delete_mode:
            # 检查行号是否在有效范围内
            if line_to_delete is None or line_to_delete < 1:
                await ankaget.finish("行号必须大于0")
                return

            if line_to_delete > total_lines:
                await ankaget.finish(
                    f"行号 {line_to_delete} 超出文件范围（总共 {total_lines} 行）"
                )
                return

            # 确认要删除的行内容
            line_content = lines[line_to_delete - 1].strip()  # 行号从1开始，索引从0开始

            # 删除指定行
            del lines[line_to_delete - 1]

            # 将剩余内容写回文件（使用UTF-8编码）
            with data_file.open("w", encoding="utf-8") as f:
                f.writelines(lines)

            # 更新总行数
            new_total = len(lines)

            await ankaget.finish(
                f"已删除安价 '{ak_name}' 的第 {line_to_delete} 行：\n"
                f"删除内容：{line_content}\n"
                f"剩余 {new_total} 行记录"
            )
            return

        # 显示模式（原有逻辑）
        if total_lines == 0:
            await ankaget.finish(f"安价 '{ak_name}' 还没有任何内容")
            return

        # 构建回复消息
        reply_msg = f"安价 '{ak_name}' 内容：\n"

        if lines_to_read is not None:
            # 按行数模式处理
            if total_lines <= lines_to_read:
                reply_msg += f"（全部 {total_lines} 条记录）\n"
                start = 0
                end = total_lines
            else:
                reply_msg += f"（最近 {lines_to_read} 条，共 {total_lines} 条）\n"
                start = max(0, total_lines - lines_to_read)
                end = total_lines
        else:
            # 按范围模式处理
            # 调整起始行和结束行（用户输入的行号是从1开始的）
            # 如果 start_line 或 end_line 为 None，则给予合理默认值，避免对 None 执行算术运算
            if start_line is None:
                start_line = 1
            if end_line is None:
                end_line = total_lines

            start = max(0, start_line - 1)
            end = min(total_lines, end_line)

            # 验证范围是否有效
            if start >= total_lines:
                await ankaget.finish(
                    f"起始行 {start_line} 超出文件范围（总共 {total_lines} 行）"
                )
                return
            if start >= end:
                await ankaget.finish(
                    f"范围无效：起始行 {start_line} 大于等于结束行 {end_line}"
                )
                return

            reply_msg += f"（第 {start_line} 到 {end_line} 行，共 {total_lines} 行）\n"

        # 获取要显示的行
        if lines_to_read is not None:
            # 按行数模式：显示最后N行
            lines_to_display = lines[start:end]
            start_line_num = start + 1  # 显示的行号从1开始
        else:
            # 按范围模式：显示指定范围
            lines_to_display = lines[start:end]
            # 确保 start_line 为整数（避免类型检查器认为它可能为 None）
            start_line_num = int(start_line) if start_line is not None else 1

        # 添加行号
        for i, line in enumerate(lines_to_display, start=start_line_num):
            reply_msg += f"{i}. {line.strip()}\n"

        # 在显示模式下，添加删除提示
        reply_msg += f"\n提示：使用 'akget {ak_name} -行号' 删除指定行（例如：akget {ak_name} -1 删除第1行）"

        # 如果记录太多，可能需要分割发送（这里假设不超过消息长度限制）
        await ankaget.finish(reply_msg)

    except FinishedException:
        # 如果是 FinishedException，说明已经调用了 finish()，直接重新抛出
        raise
    except Exception as e:
        # 只有其他异常才显示错误消息
        await ankaget.finish(f"操作失败: {str(e)}")
