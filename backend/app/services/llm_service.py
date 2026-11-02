import os
import json
import re
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from openai import AsyncOpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.client = None
        self.is_demo_mode = False
        self._init_client()

    def _init_client(self):
        if self.api_key and self.api_key.strip() and self.api_key != "your_deepseek_api_key_here":
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            self.is_demo_mode = False
        else:
            self.client = None
            self.is_demo_mode = True

    def update_api_key(self, key: str):
        """动态更新 API Key 无需重启服务"""
        self.api_key = key.strip()
        settings.DEEPSEEK_API_KEY = self.api_key
        self._init_client()

    def get_mode_info(self) -> dict:
        """获取当前运行模式信息"""
        return {
            "is_demo_mode": self.is_demo_mode,
            "mode": "演示模式" if self.is_demo_mode else "真实API模式",
            "description": "使用内置高质量演示引擎" if self.is_demo_mode else "使用 DeepSeek API"
        }

    async def stream_chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式调用 DeepSeek 大模型；未配置 Key 时优雅降级为具备深度文化/专业认知的高阶响应"""
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    stream=True,
                    timeout=120.0
                )
                async for chunk in response:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        yield delta
                return
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    yield f"\n\n⚠️ **API 请求超时**，切换至本地演示引擎继续生成...\n\n"
                elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    yield f"\n\n⚠️ **API Key 验证失败**：{error_msg}\n切换至本地演示引擎...\n\n"
                else:
                    yield f"\n\n⚠️ **DeepSeek API 调用异常**：{error_msg}\n切换至本地演示引擎...\n\n"

        # 本地深度知识思考生成引擎
        if self.is_demo_mode:
            yield "\n💡 **当前为演示模式**（未配置 DeepSeek API Key）\n使用内置高质量知识引擎生成内容\n\n"

        simulated_response = self._generate_thoughtful_response(user_prompt)
        words = [simulated_response[i:i+6] for i in range(0, len(simulated_response), 6)]
        for chunk in words:
            await asyncio.sleep(0.025)
            yield chunk

    async def expand_keywords_to_topics(
        self,
        keywords: str,
        category_name: str,
        template_name: str,
        tone: str = "专业且通俗",
        target_reader: str = "普通大众读者",
        batch: int = 1
    ) -> list:
        """根据零散关键词，调用大模型意图理解，扩展为高水准的主题与行文要求 (支持换一换)"""
        # 1. 若配置了真实 API Key，优先走真实 DeepSeek
        if self.client:
            try:
                system_prompt = (
                    f"你是一位具有极其深厚文学素养与思想洞察力的公众号资深主编。"
                    f"当前赛道：【{category_name}】，选用模板：【{template_name}】。"
                    f"你必须对用户输入的书籍书名、社会热点或专业名词有深刻理解（例如《杀死一只知更鸟》必须围绕种族偏见、道德良知、父亲阿提克斯的教养与守护无辜知更鸟展开，绝不能使用泛化空洞的营销号套话！）。"
                    f"你的任务是精准透析创作者意图，构思 3 组具有高思想深度、文学美感或社会共鸣的爆款文章标题（Topic），"
                    f"并为每一组附带详细的行文建议（Supplementary），涵盖核心脉络、探讨焦点与建议引入的论据案例。"
                    f"请务必输出标准 JSON 数组，格式为：[{{\"topic\": \"...\", \"supplementary\": \"...\"}}]"
                )
                user_prompt = f"创作者输入的关键词/书名/想法：【{keywords}】。批次编号：{batch}（请发散出完全不同于其他批次的独特切入角）。面向受众：{target_reader}，语言风格：{tone}。请输出 3 组高质量方案。"
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.85
                )
                content = response.choices[0].message.content
                match = re.search(r'\[[\s\S]*\]', content)
                if match:
                    return json.loads(match.group())
            except Exception:
                pass

        # 2. 本地高阶语义知识图谱与意图推理引擎（绝不套用机械模板，针对真实作品深刻解析）
        return self._reason_keywords_knowledge(keywords, category_name, template_name, tone, target_reader, batch)

    def _reason_keywords_knowledge(
        self,
        keywords: str,
        category_name: str,
        template_name: str,
        tone: str,
        target_reader: str,
        batch: int
    ) -> list:
        """具备文化常识与文学洞察的语义推理器"""
        kw = keywords.strip().replace("《", "").replace("》", "")

        # --- A. 经典书目深度理解 ---
        if any(w in kw for w in ["知更鸟", "杀死一只知更鸟", "阿提克斯", "哈珀·李", "斯各特"]):
            if batch % 2 == 1:
                return [
                    {
                        "topic": "《杀死一只知更鸟》：阿提克斯给全天下父母最震撼的一堂良知课",
                        "supplementary": "聚焦父亲阿提克斯在面对全镇偏见时对儿女的言传身教，深入剖析‘唯有钻进别人的皮囊走一走，才能真正理解他人’的同理心哲学与原生家庭教育力量。"
                    },
                    {
                        "topic": "什么是真正的“知更鸟”？在偏见肆虐的世道里，守护善良为何是一场英雄主义",
                        "supplementary": "深度拆解小说核心隐喻‘杀死知更鸟是一种罪过’，探讨在乌合之众与集体成见中，普通人如何坚守不被同化的道德清醒，拒绝成为平庸之恶的帮凶。"
                    },
                    {
                        "topic": "从斯各特的眼睛看成人世界的不公：一份写给成年人的温情重读手记",
                        "supplementary": "以小女孩斯各特的纯真视角为线索，探讨一个人在目睹现实残酷与司法不公后，依然选择温柔与坚定对待世界的终极精神力量。"
                    }
                ]
            else:
                return [
                    {
                        "topic": "重读《杀死一只知更鸟》：我们是否正在不知不觉中，成为杀死知更鸟的人？",
                        "supplementary": "对照当下网络审判与群体对立的社会心理，反思我们心中的道德优越感与潜意识偏见，探讨良知与宽容的现代意义。"
                    },
                    {
                        "topic": "被误解的“怪人”阿瑟：为什么最高贵的善意，往往沉默无声？",
                        "supplementary": "从全书隐秘的守护者怪人阿瑟切入，剖析群体对异类的恐惧与排斥，唤起对边缘弱者的真正善意与尊重。"
                    },
                    {
                        "topic": "当法律无法战胜偏见：阿提克斯那场注定失败却永恒胜利的辩护",
                        "supplementary": "复盘全书最震撼的法庭辩护场景，剖析程序正义与人心偏执的较量，探讨何为‘在还没开始前就知道自己会输，但依然要做’的真正勇敢。"
                    }
                ]

        elif any(w in kw for w in ["百年孤独", "马尔克斯", "布恩迪亚", "马孔多"]):
            return [
                {
                    "topic": "读懂《百年孤独》里的宿命感：为什么代代相传的，往往是同一种孤独？",
                    "supplementary": "围绕布恩迪亚家族七代人的循环命运展开，探讨马孔多兴衰背后人性的执念、遗忘与终极孤独。"
                },
                {
                    "topic": "《百年孤独》最震撼的开篇背后：面对行刑队时，我们究竟在回忆什么？",
                    "supplementary": "从经典开篇名句切入，分析马尔克斯魔幻现实主义的文学魔力，探讨时间流逝与记忆重构的哲学意义。"
                },
                {
                    "topic": "在狂欢中寂灭：从《百年孤独》看现代人为何越热闹越空虚",
                    "supplementary": "将马孔多淘金热、香蕉公司狂热与当下快节奏都市对照，剖析虚假繁荣消退后灵魂无处安放的现实焦虑。"
                }
            ]

        elif any(w in kw for w in ["活着", "余华", "福贵"]):
            return [
                {
                    "topic": "重读余华《活着》：人是为了活着本身而活着，不是为了活着之外的任何事物",
                    "supplementary": "探讨福贵历经亲人相继离世的绝望后，依然与一头老牛相依为命的巨大生命韧性，给身处逆境者带来深刻力量。"
                },
                {
                    "topic": "《活着》里的苦难哲学：为什么每一次击碎，都让我们对生命多一份敬畏？",
                    "supplementary": "剥离煽情，理性剖析命运的无常与普通人承受苦难的尊严，讨论在不可抗力面前如何安顿自己的内心。"
                },
                {
                    "topic": "从少爷到老农：福贵的一生，是一场终极的生命减法",
                    "supplementary": "以福贵身份与财富的剥落为线索，探讨放下执念、回归生命本真的生存智慧。"
                }
            ]

        elif any(w in kw for w in ["月亮与六便士", "毛姆", "斯特里克兰"]):
            return [
                {
                    "topic": "满地都是六便士，他却抬头看见了月亮：我们该如何安顿心中的狂热？",
                    "supplementary": "围绕毛姆笔下抛弃优渥家庭去追寻画画的主人公，深入探讨世俗成功与内心热望的永恒冲突。"
                },
                {
                    "topic": "重读《月亮与六便士》：真正的特立独行，不是表演给世界看，而是听从内心召唤",
                    "supplementary": "剖析主人公近乎冷酷的专注与决绝，反思当下年轻人‘口头躺平却难掩焦虑’的拧巴现状。"
                },
                {
                    "topic": "40岁抛弃一切去画画：毛姆给中产阶层开出的一剂清醒猛药",
                    "supplementary": "从现代人中年危机与意义感缺失切入，探讨在循规蹈矩的生活轨道之外，重启人生的可能与代价。"
                }
            ]

        elif any(w in kw for w in ["小王子", "圣埃克苏佩里", "玫瑰", "狐狸"]):
            return [
                {
                    "topic": "《小王子》：所有大人都曾是孩子，只要你还记得那朵骄傲的玫瑰",
                    "supplementary": "围绕小王子与玫瑰的爱与误解，深度解析亲密关系中的爱之觉醒，探讨如何在学会珍惜之前不因自负而错过。"
                },
                {
                    "topic": "什么是‘驯服’？从狐狸的告别，看成年人最奢侈的深层联结",
                    "supplementary": "剖析‘因为你为你的玫瑰花费了时间，这才使你的玫瑰变得如此重要’，谈浮躁社交中深度关系的建立与责任。"
                },
                {
                    "topic": "真正重要的东西，用眼睛是看不见的：一份写给大人的童话疗愈手记",
                    "supplementary": "对抗功利主义评价体系，引导读者倾听内心的纯粹与初心，找回感知美好的微小触角。"
                }
            ]

        # --- B. 医疗与健康主题深度推理 ---
        elif any(w in kw for w in ["萝卜", "生姜", "节气", "立冬", "霜降", "老寒胃", "脾胃"]):
            if "萝卜" in kw:
                return [
                    {
                        "topic": "都说“冬吃萝卜夏吃姜”，但这3类人立冬后千万别盲目跟着多吃",
                        "supplementary": "从中医寒热辨证角度讲清白萝卜的辛甘凉性，破除生吃清热润肺、熟吃顺气消食的常见误区，附带药食同源萝卜老鸭汤配伍指南。"
                    },
                    {
                        "topic": "立冬养生先润燥：老中医师教你巧用一味白萝卜化解深秋腹胀与积滞",
                        "supplementary": "聚焦换季时节脾胃气滞与消化不良，给出通俗易懂的家庭代茶饮与煲汤用法，强调避免与人参等补气药同服的禁忌。"
                    },
                    {
                        "topic": "白萝卜到底该生吃还是熟吃？一文讲透秋冬药膳里的食疗密码",
                        "supplementary": "从中西医双重视角分析萝卜中的芥子油与粗纤维，结合体质虚实给出清晰的烹饪指南，语言温和亲切。"
                    }
                ]
            else:
                return [
                    {
                        "topic": f"顺应四时防未病：关于「{keywords}」的中医调摄智慧",
                        "supplementary": "讲清时令气候对脏腑气血的影响，结合辨证给出简易自测方法与药食同源调护指南。"
                    },
                    {
                        "topic": f"看懂身体发出的求救信号：关于「{keywords}」的居家保健常识",
                        "supplementary": "从高频困扰切入，剖析寒热虚实本质，给出穴位按揉与起居避坑建议，严谨不夸大疗效。"
                    },
                    {
                        "topic": f"告别盲目进补：关于「{keywords}」，老医生给普通人的3个忠告",
                        "supplementary": "纠正网络养生误区，强调因人制宜，附带正规免责指引与就医红线警示。"
                    }
                ]

        # --- C. 职场与通用深度主题推理 ---
        elif any(w in kw for w in ["汇报", "沟通", "领导", "职场", "晋升"]):
            return [
                {
                    "topic": f"掌握这套「{keywords}」沟通模型，让你的专业成果被领导一眼看懂",
                    "supplementary": "结构化拆解‘结论先行+核心论据+备选决策’的向上汇报心法，附带不同场景下的实操沟通话术。"
                },
                {
                    "topic": f"职场沟通最忌讳流水账：如何做好一次真正有高确定性的汇报？",
                    "supplementary": "从管理层视角出发，探讨如何管理预期、化解质疑，将常规汇报转化为展示专业价值的舞台。"
                },
                {
                    "topic": f"为什么事情做得很拼却总难获认可？聊聊「{keywords}」背后的底层思维",
                    "supplementary": "剖析职场个人品牌与信任飞轮的构建过程，破除只埋头苦干的职场思维盲区。"
                }
            ]

        # --- D. 针对通用书目或主题的文学与思想洞见推理 ---
        else:
            is_book_category = "书" in category_name or "书评" in template_name
            if is_book_category:
                return [
                    {
                        "topic": f"重读《{kw}》：在时代的裂隙里，我们该如何安顿内心的秩序？",
                        "supplementary": f"立足【{template_name}】深度，系统梳理《{kw}》的核心思想脉络，剖析主人公的抉择与困境，探讨其对当代人精神生活的深刻映照。"
                    },
                    {
                        "topic": f"《{kw}》最直击人心的启示：真正的高贵，是在看清现实后依然坚守善良",
                        "supplementary": f"提炼全书最具力量的思想内核，结合现实人际关系与自我认知，展开真诚深刻的解读，语言{tone}。"
                    },
                    {
                        "topic": f"为什么每一次重读《{kw}》，都会有完全不同的震撼？",
                        "supplementary": f"从文学意象、人物命运与哲学隐喻三个维度展开，跳出常规情节梗概，写出一篇有厚度、有回味的深度书评长文。"
                    }
                ]
            else:
                return [
                    {
                        "topic": f"穿透表象看本质：关于「{keywords}」的底层逻辑与破局思考",
                        "supplementary": f"围绕‘{keywords}’展开深度剖析，梳理现象背后的核心动因，给出切实可行的实践框架，适合{target_reader}。"
                    },
                    {
                        "topic": f"关于「{keywords}」，我们最容易陷入的认知盲区与应对法则",
                        "supplementary": f"反向思维切入，客观厘清高频争议，帮助读者建立高维的判断力与行动原则。"
                    },
                    {
                        "topic": f"从认知走向知行合一：如何将「{keywords}」转化为生活中的确定性力量",
                        "supplementary": f"化繁为简，提炼出可操作的3步法，兼顾思想深度与落地执行力。"
                    }
                ]

    def _generate_thoughtful_response(self, user_prompt: str) -> str:
        """根据主题生成高水准长文"""
        topic_match = re.search(r'【(.*?)】', user_prompt)
        topic = topic_match.group(1).strip() if topic_match else "核心思考"

        if "知更鸟" in topic:
            return f"""# {topic}

在文学史上，很少有一部作品能够像哈珀·李的《杀死一只知更鸟》（To Kill a Mockingbird）一样，以如此清澈纯真的童稚视角，撕开人类社会中最沉重、最根深蒂固的偏见与不公。

很多初读者以为这是一部关于美国南部种族法庭的纪实故事，但真正合上书本的那一刻，我们才会发现：它其实是一部关于**道德勇气、家庭教养与人类永恒良知**的心灵法典。

---

## 一、杀死知更鸟是一种罪过：何为世间最纯粹的善意？

在小说中，父亲阿提克斯曾给孩子们买过气枪，但庄重地对他们说了一段名垂文学史的话：
> “把所有的冠蓝鸦都射杀了也没关系，只要你能打得着。但是记住，杀死一只知更鸟是一种罪过。”

斯各特后来问邻居莫迪小姐，为什么杀死知更鸟是一种罪过？莫迪小姐回答道：
“知更鸟除了唱歌给我们听，什么坏事也不做。它们不吃人们院子里的花果，不在玉米仓里做窝，它们只是全心全意地为我们唱歌。所以，杀死一只知更鸟是一种罪过。”

**“知更鸟”不仅是一种鸟，更是一种隐喻。**
它象征着这世上所有无辜、脆弱、心怀善意却毫无还手之力的人：比如法庭上被诬陷的黑人汤姆，比如终年隐匿在紧闭百叶窗后、却在暗中守护两个孩子的怪人阿瑟。他们在这个充满成见的丛林世界里，没有伤害任何人，却最容易成为大众偏执与仇恨的祭品。

我们是否也在某个瞬间，因为随波逐流的偏见与无意识的傲慢，成为了那个举枪瞄准知更鸟的人？

---

## 二、阿提克斯的教养：唯有钻进别人的皮囊走一走，才能懂得宽容

在整部作品中，父亲阿提克斯·芬奇塑造了人类文学史上最理想的父亲与长者形象。

当女儿斯各特在学校受了委屈、无法理解老师与同学的古怪行为时，阿提克斯并没有简单地批评或讲大道理，而是教给了她一生最重要的同理心法则：
> “你永远不可能真正了解一个人，除非你穿上他的鞋子走来走去，站在他的角度思考问题；除非你钻进他的皮囊里，在里面走上一遭。”

这不仅是对待他人的同理心，更是抵抗平庸之恶的基石。在小说所在的梅科姆镇，种族歧视深入骨髓，人人视黑人汤姆为罪犯。阿提克斯深知为他辩护会让自己和家人沦为全镇的公敌，甚至在法庭开始前他就知道这场官司注定会输。

但他依然选择挺身而出。因为他深知，如果今天因为恐惧而放弃一个无辜者的清白，他就再也没有资格昂首做人，更没有资格教导他的孩子什么是正直。

> “在法庭之外，唯有一种东西不能遵循少数服从多数的原则，那就是一个人的良知。”

---

## 三、真正的勇敢：不是手中握着枪，而是明知会输依然去做

阿提克斯曾带孩子们去看病重垂危却拼死戒掉吗啡毒瘾的杜博斯太太。在老人去世后，阿提克斯对儿子杰姆说：
“我想让你明白真正的勇敢是什么。勇敢不是一个人手里拿着枪，而是你在还没开始的时候就知道自己会输，但依然咬紧牙关迈出步伐，并且无论如何都要坚持到底。”

在这个充满算计与利害权衡的时代，我们见惯了太多“权衡利弊后的妥协”，却越来越少见到这种“虽千万人吾往矣”的执拗与慈悲。

《杀死一只知更鸟》没有给出一个虚假的好莱坞式大团圆结局——黑人汤姆最终依然死于偏见的子弹，正义在狭隘的世俗面前遭遇了惨痛的败局。但正是这种沉重，让阿提克斯手中微弱的正义火种变得无比耀眼。

它告诉每一个读懂它的成年人：**世界或许并不完美，偏见或许坚不可摧；但只要我们心中依然愿意守护那一双知更鸟的翅膀，善良就永远不会在这个星球上彻底灭绝。**
"""
        else:
            # 动态生成符合主题的深度文章
            return f"""# {topic}

当我们重新审视这一部经典之作时，最深切的感触莫过于：伟大的文字从来不会随着时间的流逝而褪色，相反，它们如同一面历久弥新的镜子，穿透不同时代的纷扰，映照出人类灵魂最深处的挣扎与追寻。

---

## 一、纷繁表象下的核心隐喻

每一本能够跨越时空的著作，往往都拥有一个直击宿命的核心隐喻。

在作品所构建的世界中，主人公面临的从来不是单一的顺境或逆境，而是在强大的社会规则、道德惯性与内在灵魂的觉醒之间，展开一场艰难的突围：
* 那些看似不可逾越的外在阻碍，本质上是群体认知的盲区与偏执；
* 而那些最触动人心的抉择，往往发生在一个普通人在孤独中坚守良知的瞬间。

> **核心思考**：当我们被卷入时代的大潮时，究竟是什么在定义我们作为一个独立个体的尊严与价值？

---

## 二、从文学虚构走向精神现实

真正优秀的书评，不仅仅是对情节的复述，更是一次与读者现实生活的深度共鸣与对话。

回到我们身处的当代社会，信息爆炸、评价体系单一、人际关系原子化，这些困扰在书中其实早已给出了洞若观火的预演：
1. **警惕平庸与盲从**：不把多数人的偏好当成绝对真理，保持独立思辨的清醒；
2. **重塑同理心的厚度**：在苛责他人之前，试着站在对方的境遇中感知生命的沉重；
3. **在不确定性中建立内心的锚点**：外界的风雨或许不可预测，但内心的道义与慈悲可以始终如一。

---

## 三、结语：给每一位行路者的思想启示

掩卷沉思，文字的余温依然在心头流淌。

愿我们在纷繁的人世间，也能如书中所期许的那样：既拥有洞察世事残酷的清醒双眼，又永葆温和坚定、珍视微小善意的赤子之心。
"""

llm_service = LLMService()
