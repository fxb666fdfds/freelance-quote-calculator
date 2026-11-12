#!/usr/bin/env python3
"""接单报价计算器：计算单笔收益、时薪及月目标所需订单数。仅使用标准库。"""

import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR


def non_negative(value):
    """拒绝负数、NaN、Infinity 以及过大的输入。"""
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("请输入有效数字") from exc
    if not number.is_finite() or number < 0 or number > Decimal("1000000000"):
        raise argparse.ArgumentTypeError("请输入 0 到 1000000000 之间的有限数字")
    if number != number.quantize(Decimal("0.0001")):
        raise argparse.ArgumentTypeError("最多保留四位小数")
    return number


def positive(value):
    number = non_negative(value)
    if number == 0:
        raise argparse.ArgumentTypeError("必须大于 0")
    return number


def percentage(value):
    number = non_negative(value)
    if number >= 100:
        raise argparse.ArgumentTypeError("手续费比例必须小于 100")
    return number


def calculate(price, hours, cost, fee_rate, target, available_hours):
    fee = price * fee_rate / 100
    profit = price - cost - fee
    capacity = int((available_hours / hours).to_integral_value(rounding=ROUND_FLOOR))
    if target == 0:
        orders = 0
    elif profit > 0:
        orders = int((target / profit).to_integral_value(rounding=ROUND_CEILING))
    else:
        orders = None
    return {
        "fee": fee,
        "profit": profit,
        "hourly": profit / hours,
        "orders": orders,
        "required_hours": None if orders is None else orders * hours,
        "capacity": capacity,
        "capacity_profit": capacity * profit,
    }


def main():
    parser = argparse.ArgumentParser(
        description="估算接单收益；所有金额使用同一种货币，工时包含沟通与修改。"
    )
    parser.add_argument("--price", required=True, type=positive, help="每单报价")
    parser.add_argument("--hours", required=True, type=positive, help="每单总工时")
    parser.add_argument("--cost", type=non_negative, default=Decimal("0"), help="每单直接成本，默认 0")
    parser.add_argument("--fee-rate", type=percentage, default=Decimal("0"), help="平台手续费百分比，如 5 表示 5%%")
    parser.add_argument("--target", type=non_negative, default=Decimal("3000"), help="每月收益目标，默认 3000")
    parser.add_argument("--available-hours", type=non_negative, default=Decimal("60"), help="每月可用工时，默认 60")
    args = parser.parse_args()
    result = calculate(args.price, args.hours, args.cost, args.fee_rate, args.target, args.available_hours)

    print("\n接单报价计算器")
    print(f"每单报价：{args.price:.2f} 元")
    print(f"每单成本：{args.cost:.2f} 元；平台手续费：{result['fee']:.2f} 元")
    print(f"每单收益：{result['profit']:.2f} 元")
    print(f"实际时薪：{result['hourly']:.2f} 元/小时")
    if result["orders"] is None:
        print("当前每单收益不大于 0，无法通过增加订单达到正收益目标。")
    else:
        print(f"月目标 {args.target:.2f} 元：至少需要 {result['orders']} 单")
        print(f"所需工时：{result['required_hours']:.2f} 小时")
        if result["required_hours"] > args.available_hours:
            print("按当前报价和工时，月目标超出了你的可用时间。")
    print(f"按每月 {args.available_hours:.2f} 小时，最多可完成 {result['capacity']} 单")
    print(f"全部完成时的月收益：{result['capacity_profit']:.2f} 元")
    print("以上收益仅扣除所填直接成本与平台手续费。\n")


if __name__ == "__main__":
    main()
