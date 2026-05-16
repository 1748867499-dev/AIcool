"""
智能意向评估 Agent
使用长链推理（Chain-of-Thought）评估客户意向等级
"""

import json
from typing import Dict, Tuple
from datetime import datetime, timedelta


class IntentScorer:
    """客户意向评估 Agent"""
    
    def __init__(self):
        self.weights = {
            "browse_duration": 0.15,
            "consult_count": 0.20,
            "showing_count": 0.25,
            "price_sensitivity": 0.10,
            "response_speed": 0.10,
            "budget_match": 0.10,
            "urgency_score": 0.10
        }
    
    def evaluate(self, customer_features: Dict) -> Dict:
        """
        使用长链推理评估客户意向
        
        Args:
            customer_features: 客户行为特征字典
            
        Returns:
            {"level": "high/medium/low", "confidence": 0.0-1.0, "reasoning": "推理过程"}
        """
        reasoning_steps = []
        
        # Step 1: 浏览行为分析
        browse_score = self._analyze_browse(customer_features)
        reasoning_steps.append(
            f"1. 客户浏览了 {customer_features.get('browse_count', 0)} 套房源，"
            f"平均浏览时长 {customer_features.get('browse_duration', 0)//60} 分钟/套"
            f"→ {'说明客户有明确需求，不是随便看看' if browse_score > 0.6 else '浏览行为一般，需进一步观察'}"
        )
        
        # Step 2: 咨询行为分析
        consult_score = self._analyze_consult(customer_features)
        reasoning_steps.append(
            f"2. 客户咨询了 {customer_features.get('consult_count', 0)} 次，"
            f"问题集中在 {customer_features.get('consult_topics', '价格、位置')}"
            f"→ {'说明客户已进入决策阶段' if consult_score > 0.6 else '咨询深度不足，需引导'}"
        )
        
        # Step 3: 带看行为分析
        showing_score = self._analyze_showing(customer_features)
        reasoning_steps.append(
            f"3. 客户预约了 {customer_features.get('showing_count', 0)} 次带看，"
            f"准时率 {customer_features.get('showing_punctuality', 0)*100:.0f}%"
            f"→ {'说明客户诚意度高' if showing_score > 0.6 else '带看参与度一般'}"
        )
        
        # Step 4: 预算匹配分析
        budget_score = self._analyze_budget(customer_features)
        reasoning_steps.append(
            f"4. 客户预算与房源价格匹配度 {customer_features.get('budget_match', 0)*100:.0f}%"
            f"→ {'经济能力匹配，可推进签约' if budget_score > 0.7 else '预算偏低，需调整推荐'}"
        )
        
        # Step 5: 紧急程度分析
        urgency_score = self._analyze_urgency(customer_features)
        reasoning_steps.append(
            f"5. 客户入住时间要求 {customer_features.get('move_in_days', 30)} 天内"
            f"→ {'时间紧迫，需优先跟进' if urgency_score > 0.7 else '时间充裕，可长期培育'}"
        )
        
        # 综合评分
        total_score = (
            browse_score * self.weights["browse_duration"] +
            consult_score * self.weights["consult_count"] +
            showing_score * self.weights["showing_count"] +
            (1 - customer_features.get("price_sensitivity", 0.5)) * self.weights["price_sensitivity"] +
            (1 - min(customer_features.get("response_speed", 300)/600, 1)) * self.weights["response_speed"] +
            budget_score * self.weights["budget_match"] +
            urgency_score * self.weights["urgency_score"]
        )
        
        # 确定意向等级
        if total_score >= 0.7:
            level = "high"
            confidence = min(total_score + 0.1, 0.95)
        elif total_score >= 0.4:
            level = "medium"
            confidence = total_score
        else:
            level = "low"
            confidence = 1 - total_score
        
        reasoning_steps.append(
            f"\n综合评分: {total_score:.2f} → 意向等级: {level.upper()}, 置信度: {confidence:.0%}"
        )
        
        return {
            "level": level,
            "confidence": round(confidence, 2),
            "score": round(total_score, 2),
            "reasoning": "\n".join(reasoning_steps)
        }
    
    def _analyze_browse(self, features: Dict) -> float:
        """分析浏览行为"""
        duration = features.get("browse_duration", 0)
        count = features.get("browse_count", 0)
        
        if count == 0:
            return 0.0
        
        avg_duration = duration / count if count > 0 else 0
        score = min(avg_duration / 300, 1.0)  # 5分钟为满分
        score *= min(count / 5, 1.0)  # 浏览5套以上为满分
        
        return score
    
    def _analyze_consult(self, features: Dict) -> float:
        """分析咨询行为"""
        count = features.get("consult_count", 0)
        
        if count == 0:
            return 0.0
        
        score = min(count / 5, 1.0)  # 咨询5次以上为满分
        
        # 如果咨询了价格、付款方式等深度问题，加分
        topics = features.get("consult_topics", [])
        deep_topics = ["价格", "付款", "合同", "入住时间"]
        deep_count = sum(1 for t in topics if any(d in t for d in deep_topics))
        score += min(deep_count * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _analyze_showing(self, features: Dict) -> float:
        """分析带看行为"""
        count = features.get("showing_count", 0)
        punctuality = features.get("showing_punctuality", 0)
        
        if count == 0:
            return 0.0
        
        score = min(count / 3, 1.0) * 0.7  # 带看3次以上为满分
        score += punctuality * 0.3  # 准时率权重
        
        return score
    
    def _analyze_budget(self, features: Dict) -> float:
        """分析预算匹配度"""
        match = features.get("budget_match", 0)
        return match
    
    def _analyze_urgency(self, features: Dict) -> float:
        """分析紧急程度"""
        days = features.get("move_in_days", 30)
        
        if days <= 7:
            return 1.0
        elif days <= 14:
            return 0.8
        elif days <= 30:
            return 0.6
        else:
            return 0.3


# 示例使用
if __name__ == "__main__":
    scorer = IntentScorer()
    
    # 模拟一个高意向客户
    customer = {
        "browse_duration": 1800,  # 30分钟
        "browse_count": 8,
        "consult_count": 5,
        "consult_topics": ["价格", "付款方式", "入住时间", "物业费"],
        "showing_count": 2,
        "showing_punctuality": 1.0,
        "price_sensitivity": 0.3,
        "response_speed": 120,
        "budget_match": 0.85,
        "urgency_score": 0.8,
        "move_in_days": 10
    }
    
    result = scorer.evaluate(customer)
    
    print("=" * 60)
    print("客户意向评估报告")
    print("=" * 60)
    print(f"\n意向等级: {result['level'].upper()}")
    print(f"置信度: {result['confidence']:.0%}")
    print(f"综合评分: {result['score']:.2f}")
    print(f"\n推理过程:\n{result['reasoning']}")
    print("=" * 60)
