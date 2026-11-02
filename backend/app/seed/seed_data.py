import asyncio
import os
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.config import settings
from app.models.category import Category, Template
from app.models.prompt_config import PromptConfig
from app.models.article import Article, OutlineCandidate
from app.models.article_history import ArticleHistory

# 默认医疗健康合规免责声明
TCM_DISCLAIMER = "【健康提示】本文仅供医学常识与健康养生科普，不能替代临床诊疗。个人体质有异，如遇身体不适，请前往正规医疗机构遵医嘱就医。"

# 预置赛道
CATEGORIES_DATA = [
    {"id": "tcm_health", "name": "中医健康 / 医疗养生", "icon": "HeartPulse", "sort_order": 1, "description": "适合专业医生、中医调理与大众健康科普"},
    {"id": "book_review", "name": "读书书评", "icon": "BookOpen", "sort_order": 2, "description": "深度书评、金句拆解与知识卡片"},
    {"id": "current_affairs", "name": "时事观点", "icon": "Flame", "sort_order": 3, "description": "热点新闻解读与独家洞察"},
    {"id": "workplace", "name": "职场成长", "icon": "Briefcase", "sort_order": 4, "description": "职场进阶、沟通法则与管理思维"},
    {"id": "emotion", "name": "情感心理", "icon": "Heart", "sort_order": 5, "description": "心理共情、亲密关系与治愈故事"},
    {"id": "tech", "name": "科技商业", "icon": "Cpu", "sort_order": 6, "description": "AI趋势、商业模式与行业研报"},
    {"id": "life", "name": "生活方式", "icon": "Coffee", "sort_order": 7, "description": "极简生活、日常美学与城市漫步"},
    {"id": "education", "name": "家庭教育", "icon": "GraduationCap", "sort_order": 8, "description": "亲子沟通、教育理念与儿童心理"},
    {"id": "culture", "name": "历史人文", "icon": "Landmark", "sort_order": 9, "description": "历史人物、传统文化与文史新读"},
    {"id": "travel", "name": "旅行游记", "icon": "Compass", "sort_order": 10, "description": "路线攻略、小众目的地与旅行随笔"},
    {"id": "operation", "name": "产品运营", "icon": "TrendingUp", "sort_order": 11, "description": "自媒体运营、用户增长与产品思考"},
    {"id": "finance", "name": "理财投资", "icon": "DollarSign", "sort_order": 12, "description": "理财规划、投资策略与财商教育"},
    {"id": "food", "name": "美食探店", "icon": "UtensilsCrossed", "sort_order": 13, "description": "美食测评、探店攻略与烹饪分享"},
    {"id": "entertainment", "name": "影视娱乐", "icon": "Film", "sort_order": 14, "description": "影评剧评、娱乐八卦与流行文化"},
    {"id": "fitness", "name": "运动健身", "icon": "Dumbbell", "sort_order": 15, "description": "健身教程、运动科学与体态管理"}
]

# 预置模板（重点丰富中医/医疗与读书赛道）
TEMPLATES_DATA = [
    # 1. 中医健康 / 医疗养生 5 大专属模板
    {
        "id": "tcm_seasonal", "category_id": "tcm_health", "name": "时令节气调理", "tag": "养生食疗", "sort_order": 1,
        "description": "结合24节气气候特点、脏腑调理与药食同源茶饮方，语言通俗亲切。",
        "outline_system": "你是一位拥有深厚中医临床经验的主任中医师兼健康自媒体专家。行文严谨权威，深入浅出。严禁绝对化词汇（如神效、包治百病），药方严格遵循卫健委‘药食同源’标准。",
        "outline_user": "请针对主题【{topic}】构思 3 组具有高点击率且严谨的公众号标题，并为每组输出详细大纲结构。\n补充要求：{supplementary}\n预期字数：约{word_count}字，风格要求：{tone}，面向受众：{target_reader}。\n请严格以 JSON 格式输出，包含 candidates: [{index, title, summary, tags, outline_sections}]。",
        "article_system": "你是一位权威温和的中医专家，善于用通俗易懂的生动比喻讲透中医病机与调理方案。每篇文章必须逻辑清晰，兼具知识增量与可操作性。",
        "article_user": "请基于选定标题【{title}】以及大纲：\n{outline}\n展开撰写完整的公众号正文（Markdown 格式）。\n要求：\n1. 字数达到约 {word_count} 字；\n2. 语言亲切通俗，避免生涩术语堆砌；\n3. 食疗茶饮方须明确用量与适用/禁忌体质；\n4. 篇尾必须由系统附带标准免责提示。",
        "append_disclaimer": True
    },
    {
        "id": "tcm_syndrome", "category_id": "tcm_health", "name": "常见病辨证科普", "tag": "病理通俗化", "sort_order": 2,
        "description": "聚焦失眠、脾胃虚弱、湿气重等常见困扰，讲清病机并给出自测与调护建议。",
        "outline_system": "你是一位中医内科临床医生，擅长将复杂的脏腑辨证（虚实寒热）转化为老百姓一听就懂的身体信号。",
        "outline_user": "请根据主题【{topic}】提供 3 组选题方案与大纲。补充说明：{supplementary}。面向：{target_reader}。以标准 JSON 结构输出。",
        "article_system": "你是一位耐心的中医名医，撰写体检或日常病症辨证长文。注重引导读者科学认识身体，防微杜渐。",
        "article_user": "根据标题【{title}】和大纲【{outline}】撰写约 {word_count} 字的科普长文。包含：高频痛点共鸣、病机生动拆解、简易体质自测、居家调护方案。",
        "append_disclaimer": True
    },
    {
        "id": "tcm_herb_point", "category_id": "tcm_health", "name": "本草与穴位速懂", "tag": "单点百科", "sort_order": 3,
        "description": "针对一味药食同源中药或一个保健穴位做透彻通俗讲解，含用法与禁忌。",
        "outline_system": "你是一位中药学与经络穴位研究专家，专注通俗科普本草源流与安全用法。",
        "outline_user": "针对本草或穴位主题【{topic}】构思 3 组文章大纲，必须强调‘适合谁’与‘谁千万别碰’。以 JSON 返回。",
        "article_system": "你是一位资深中药师，用最接地气的语言普及单味药或单个穴位的安全用法。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字文章。详述其性味归经、日常巧用（如泡水搭配）、体质禁忌与误区防坑。",
        "append_disclaimer": True
    },
    {
        "id": "tcm_clinical_case", "category_id": "tcm_health", "name": "门诊医案叙事", "tag": "医患故事", "sort_order": 4,
        "description": "以隐去隐私的真实就医问诊故事开篇，引人入胜，带出深刻的防病警示与就诊建议。",
        "outline_system": "你是一位临床医生兼非虚构医疗作家，擅长以真实故事引发读者健康反思。",
        "outline_user": "针对病例主题【{topic}】设计 3 组叙事型选题，突出波折、医者探因与最终启示。以 JSON 输出。",
        "article_system": "你是一位饱含人文关怀的医生，用第一人称或第三人称讲述真实的门诊故事与医学启示。",
        "article_user": "根据选定标题【{title}】和大纲撰写约 {word_count} 字的医案随笔。叙事生动，剖析严谨，给出大众预防之道。",
        "append_disclaimer": True
    },
    {
        "id": "tcm_myth_busting", "category_id": "tcm_health", "name": "中西医健康辟谣", "tag": "避坑指南", "sort_order": 5,
        "description": "针对朋友圈与网络上的伪养生谣言，用中西医双重视角进行有理有据的权威破解。",
        "outline_system": "你是一位具备全科医学与中医功底的科普辟谣专家，逻辑犀利，论据扎实。",
        "outline_user": "针对养生误区【{topic}】提供 3 组具有抓人眼球辟谣标题与大纲架构。以 JSON 返回。",
        "article_system": "你是一位实事求是的医学辟谣主笔，客观指出谣言的漏洞及潜在危害，并给出正确应对方式。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字的辟谣长文。列举错误观念、从病理角度揭露危害、给出替代科学方案。",
        "append_disclaimer": True
    },

    # 2. 读书书评代表性模板
    {
        "id": "book_deep_review", "category_id": "book_review", "name": "深度书评", "tag": "经典通用", "sort_order": 1,
        "description": "系统梳理作品的核心观点与现实意义，层层递进，适合高品质深度阅读者。",
        "outline_system": "你是一位知名书评人与深度阅读推广者，文笔优美深刻，善于将书中哲理与当代人生困境相连接。",
        "outline_user": "请就书目/主题【{topic}】构思 3 组深度书评标题与结构大纲。要求包含书籍核心理念与现实痛点映射。以 JSON 输出。",
        "article_system": "你是一位知名文化学者兼公号大V，撰写逻辑严谨、文笔优雅的深度书评。",
        "article_user": "根据标题【{title}】与大纲撰写约 {word_count} 字的书评长文。结合当代生活案例展开论证。",
        "append_disclaimer": False
    },
    {
        "id": "book_golden_quote", "category_id": "book_review", "name": "金句摘读", "tag": "金句解析", "sort_order": 2,
        "description": "围绕书中关键金句展开思考与生活延伸，适合轻松有趣的启发性分享。",
        "outline_system": "你是一位擅长情感共鸣与金句拆解的内容导师，善于从单句话引出深度思考。你的任务是识别并提炼书中的精华金句。",
        "outline_user": "针对书籍或作品【{topic}】设计 3 组金句摘读式大纲方案。\n\n**核心要求**：\n1. 每组方案需聚焦书中 3-5 条具有启发性的金句\n2. 为每条金句设计深度解读与生活场景延伸\n3. 面向受众：{target_reader}\n4. 语言风格：{language_style}\n5. 写作基调：{tone}\n6. 专业程度：{professionalism}\n\n补充要求：{supplementary}\n自定义需求：{custom_requirements}\n\n请严格以 JSON 格式输出，包含 candidates: [{{index, title, summary, tags, outline_sections}}]。",
        "article_system": "你是一位温暖治愈的读书博主，用轻快细腻的笔触展开金句解读。你善于将金句与读者的生活经验建立共鸣连接。",
        "article_user": "根据标题【{title}】和大纲【{outline}】撰写约 {word_count} 字的金句分享文章。\n\n**写作要求**：\n1. 逐条呈现金句原文并标注出处（页码或章节）\n2. 每条金句后附上 200-300 字的深度解读\n3. 结合当代生活场景进行延伸思考\n4. 排版格式：{formatting}\n5. 语言风格：{language_style}\n6. 专业程度：{professionalism}\n7. 写作基调：{tone}\n\n自定义需求：{custom_requirements}",
        "append_disclaimer": False
    },
    {
        "id": "book_character_analysis", "category_id": "book_review", "name": "人物解读", "tag": "人物分析", "sort_order": 3,
        "description": "聚焦书中关键人物，剖析其性格与命运，探讨对普通人生的现实启示。",
        "outline_system": "你是一位擅长心理分析与人物小传的专栏作家。",
        "outline_user": "针对人物分析主题【{topic}】生成 3 组大纲方案。以 JSON 输出。",
        "article_system": "你是一位人物传记作家，从细节入微处剖析人性与命运轨迹。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字人物解读长文。",
        "append_disclaimer": False
    },
    {
        "id": "book_thematic_thinking", "category_id": "book_review", "name": "主题思考", "tag": "主题延伸", "sort_order": 4,
        "description": "围绕书中核心主题展开，结合当下社会热点与青年现状进行综合探讨。",
        "outline_system": "你是一位敏锐的社会观察家与书评专栏作者。",
        "outline_user": "针对主题【{topic}】提供 3 组跨界探讨大纲。以 JSON 输出。",
        "article_system": "你是一位富有思想深度的评论人，探讨书中智慧在现实中的落地可能。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字文章。",
        "append_disclaimer": False
    },
    {
        "id": "book_reading_experience", "category_id": "book_review", "name": "读后感", "tag": "真实走心", "sort_order": 5,
        "description": "从个人经历与第一人称出发，分享真实的阅读体验与心智成长感悟。",
        "outline_system": "你是一位善于自我觉察与倾诉的随笔作家，注重真情实感。",
        "outline_user": "针对主题【{topic}】设计 3 组第一人称走心读后感大纲。以 JSON 输出。",
        "article_system": "你是一位真诚的写作者，用平实感人的笔调倾诉读书如何改变了自己的心境。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字走心读后感。",
        "append_disclaimer": False
    },
    {
        "id": "book_comparative_review", "category_id": "book_review", "name": "对比书评", "tag": "对比阅读", "sort_order": 6,
        "description": "将两本或多本观点互补/对立的书籍进行横向对比，碰撞出不同思想火花。",
        "outline_system": "你是一位擅长比较阅读的高阶知识博主。",
        "outline_user": "针对对比主题【{topic}】生成 3 组横向比对大纲方案。以 JSON 输出。",
        "article_system": "你是一位思维开阔的学术书评人，客观呈现不同作者观点的碰撞。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字对比书评。",
        "append_disclaimer": False
    },

    # 3. 时事观点
    {
        "id": "ca_hot_deep", "category_id": "current_affairs", "name": "热点深度解读", "tag": "深度剖析", "sort_order": 1,
        "description": "不随波逐流，从热点新闻表象挖掘背后深层社会动因与趋势。",
        "outline_system": "你是一位理性克制的时事评论主笔，擅长从喧嚣中梳理关键脉络。",
        "outline_user": "针对时事热点【{topic}】构思 3 组兼具思考力与严谨度的大纲。以 JSON 输出。",
        "article_system": "你是一位知名时评专栏作者，逻辑缜密，见解独到。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字时评文章。",
        "append_disclaimer": False
    },
    {
        "id": "ca_timeline", "category_id": "current_affairs", "name": "事件脉络复盘", "tag": "事件还原", "sort_order": 2,
        "description": "按时间线全面复盘争议事件的前因后果，提供全局视角。",
        "outline_system": "你是一位调查记者，善于抽丝剥茧还原事件全貌。",
        "outline_user": "针对热点事件【{topic}】设计 3 组复盘大纲。以 JSON 输出。",
        "article_system": "你是一位客观的特稿主笔，梳理事态演进的关键节点。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字复盘文章。",
        "append_disclaimer": False
    },

    # 4. 职场成长
    {
        "id": "wp_communication", "category_id": "workplace", "name": "职场情商沟通", "tag": "话术干货", "sort_order": 1,
        "description": "向上汇报、跨部门沟通与化解冲突的高情商实操话术。",
        "outline_system": "你是一位世界500强前高管兼职场导师，实操经验丰富。",
        "outline_user": "针对职场沟通主题【{topic}】设计 3 组具有共鸣感的大纲。以 JSON 输出。",
        "article_system": "你是一位资深职场顾问，提供结构化的沟通解法。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字职场干货文章。",
        "append_disclaimer": False
    },
    {
        "id": "wp_promotion", "category_id": "workplace", "name": "升职晋升法则", "tag": "底层逻辑", "sort_order": 2,
        "description": "拆解优秀员工与平庸员工的思维差异，提供晋升破局点。",
        "outline_system": "你是一位资深猎头与组织发展专家。",
        "outline_user": "针对主题【{topic}】构思 3 组晋升破局大纲。以 JSON 输出。",
        "article_system": "你是一位实战派职业规划师，剖析职场成长瓶颈。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字文章。",
        "append_disclaimer": False
    },

    # 5. 情感心理
    {
        "id": "em_healing", "category_id": "emotion", "name": "治愈共鸣随笔", "tag": "温暖治愈", "sort_order": 1,
        "description": "抚平焦虑，提供情绪价值与自我和解的温暖文字。",
        "outline_system": "你是一位温暖走心的心理咨询师兼散文作家。",
        "outline_user": "针对情感困扰【{topic}】生成 3 组直击人心的文章大纲。以 JSON 输出。",
        "article_system": "你是一位善于倾听的情感专栏作家，文字细腻温柔。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字疗愈长文。",
        "append_disclaimer": False
    },
    {
        "id": "em_relationship", "category_id": "emotion", "name": "亲密关系洞察", "tag": "相处之道", "sort_order": 2,
        "description": "剖析恋爱、婚姻与人际交往中的心理机制与健康边界。",
        "outline_system": "你是一位专业的情感关系咨询专家。",
        "outline_user": "针对亲密关系话题【{topic}】设计 3 组大纲。以 JSON 输出。",
        "article_system": "你是一位理性温和的心理导师，引导读者建立健康关系模式。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字文章。",
        "append_disclaimer": False
    },

    # 6. 科技商业
    {
        "id": "tech_ai_review", "category_id": "tech", "name": "AI与科技评测", "tag": "前沿应用", "sort_order": 1,
        "description": "实操评测最新 AI 工具或科技产品，赋能个人与企业效率。",
        "outline_system": "你是一位硬核科技博主与数字化转型顾问。",
        "outline_user": "针对科技主题【{topic}】构思 3 组具有高价值感的大纲。以 JSON 输出。",
        "article_system": "你是一位科技专栏作者，用通俗语言拆解复杂技术。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字评测文章。",
        "append_disclaimer": False
    },
    {
        "id": "tech_business_model", "category_id": "tech", "name": "商业模式拆解", "tag": "商业洞察", "sort_order": 2,
        "description": "深度剖析一家企业或一个新消费赛道的盈利逻辑与竞争壁垒。",
        "outline_system": "你是一位资深商业分析师与一级市场投资顾问。",
        "outline_user": "针对商业案例【{topic}】设计 3 组深度商业大纲。以 JSON 输出。",
        "article_system": "你是一位知名商业媒体主笔，剖析商业底层逻辑。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字深度研报。",
        "append_disclaimer": False
    },

    # 7. 生活方式
    {
        "id": "life_minimalist", "category_id": "life", "name": "极简生活美学", "tag": "生活哲学", "sort_order": 1,
        "description": "分享断舍离、精简生活与专注内心的生活灵感。",
        "outline_system": "你是一位极简生活家与生活美学倡导者。",
        "outline_user": "针对生活方式【{topic}】提供 3 组大纲。以 JSON 输出。",
        "article_system": "你是一位热爱生活的美学作家，文风清爽松弛。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字生活随笔。",
        "append_disclaimer": False
    },

    # 8. 家庭教育
    {
        "id": "edu_parenting", "category_id": "education", "name": "科学育儿指南", "tag": "家庭教育", "sort_order": 1,
        "description": "结合儿童发展心理学，提供不焦虑的亲子沟通与陪伴方法。",
        "outline_system": "你是一位儿童心理学专家与正面管教讲师。",
        "outline_user": "针对教育困惑【{topic}】构思 3 组科学育儿大纲。以 JSON 输出。",
        "article_system": "你是一位亲切的家庭教育导师，提供实操性极强的育儿建议。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字教育长文。",
        "append_disclaimer": False
    },

    # 9. 历史人文
    {
        "id": "cul_history_story", "category_id": "culture", "name": "历史人物沉浮", "tag": "文史新读", "sort_order": 1,
        "description": "在真实史料中打捞生动的人性细节，借古鉴今。",
        "outline_system": "你是一位文史专栏作家，擅长讲好看的历史人物故事。",
        "outline_user": "针对历史话题【{topic}】设计 3 组引人入胜的大纲。以 JSON 输出。",
        "article_system": "你是一位饱读诗书的历史作家，以生动笔触还原历史现场。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字文史文章。",
        "append_disclaimer": False
    },

    # 10. 旅行游记
    {
        "id": "trv_guide", "category_id": "travel", "name": "小众目的地探索", "tag": "旅行漫游", "sort_order": 1,
        "description": "避开人潮，寻找具有独特烟火气与自然风光的松弛之旅。",
        "outline_system": "你是一位资深旅行探险家与人文地理摄影师。",
        "outline_user": "针对目的地【{topic}】生成 3 组探索大纲。以 JSON 输出。",
        "article_system": "你是一位文字优美生动的旅行作家，描摹旅途的风景与故事。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字深度游记。",
        "append_disclaimer": False
    },

    # 11. 产品运营
    {
        "id": "op_growth", "category_id": "operation", "name": "爆款内容增长", "tag": "运营方法论", "sort_order": 1,
        "description": "复盘公众号与自媒体打造爆款文章、粉丝沉淀的操盘经验。",
        "outline_system": "你是一位头部自媒体内容操盘手与增长黑客。",
        "outline_user": "针对运营策略【{topic}】设计 3 组干货大纲。以 JSON 输出。",
        "article_system": "你是一位实战派运营导师，输出可复制的增长方法论。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字干货长文。",
        "append_disclaimer": False
    },

    # 12. 理财投资
    {
        "id": "fin_plan", "category_id": "finance", "name": "理财规划指南", "tag": "财商教育", "sort_order": 1,
        "description": "从小白到进阶的理财规划方法、投资策略与风险管理。",
        "outline_system": "你是一位持证理财规划师与投资顾问，擅长用通俗语言讲解金融知识。",
        "outline_user": "针对理财主题【{topic}】设计 3 组实用大纲。面向受众：{target_reader}，专业程度：{professionalism}。以 JSON 输出。",
        "article_system": "你是一位财商教育专家，提供可落地的理财建议。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字理财科普文章。语言风格：{language_style}，写作基调：{tone}。",
        "append_disclaimer": False
    },
    {
        "id": "fin_analysis", "category_id": "finance", "name": "投资分析", "tag": "投资策略", "sort_order": 2,
        "description": "深度分析投资标的、市场趋势与投资机会。",
        "outline_system": "你是一位资深投资分析师，具备深厚的金融市场分析能力。",
        "outline_user": "针对投资分析主题【{topic}】设计 3 组专业大纲。以 JSON 输出。",
        "article_system": "你是一位专业的投资分析师，提供客观深入的市场分析。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字投资分析文章。",
        "append_disclaimer": False
    },

    # 13. 美食探店
    {
        "id": "food_review", "category_id": "food", "name": "美食测评", "tag": "探店体验", "sort_order": 1,
        "description": "真实的探店体验、菜品测评与美食推荐。",
        "outline_system": "你是一位资深美食博主与探店达人，对美食有独到的品鉴眼光。",
        "outline_user": "针对美食探店主题【{topic}】设计 3 组吸引人的大纲。面向受众：{target_reader}，语言风格：{language_style}。以 JSON 输出。",
        "article_system": "你是一位生动有趣的美食作家，善于用文字呈现美食的色香味。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字美食测评文章。写作基调：{tone}，排版格式：{formatting}。",
        "append_disclaimer": False
    },

    # 14. 影视娱乐
    {
        "id": "film_review", "category_id": "entertainment", "name": "影评剧评", "tag": "深度解析", "sort_order": 1,
        "description": "深度剖析影视作品的艺术价值、社会意义与文化内涵。",
        "outline_system": "你是一位专业影评人与文化评论家，具备深厚的影视艺术素养。",
        "outline_user": "针对影视作品【{topic}】设计 3 组深度影评大纲。面向受众：{target_reader}，专业程度：{professionalism}。以 JSON 输出。",
        "article_system": "你是一位知名影评人，擅长从多维度解读影视作品。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字影评文章。语言风格：{language_style}，写作基调：{tone}。",
        "append_disclaimer": False
    },

    # 15. 运动健身
    {
        "id": "fitness_guide", "category_id": "fitness", "name": "健身教程", "tag": "训练指导", "sort_order": 1,
        "description": "科学的健身训练方法、营养指导与体态管理方案。",
        "outline_system": "你是一位持证健身教练与运动康复专家，熟悉运动科学与训练方法。",
        "outline_user": "针对健身主题【{topic}】设计 3 组实用训练大纲。面向受众：{target_reader}，专业程度：{professionalism}。以 JSON 输出。",
        "article_system": "你是一位专业健身教练，提供科学安全的训练指导。",
        "article_user": "根据标题【{title}】和大纲撰写约 {word_count} 字健身指导文章。语言风格：{language_style}，排版格式：{formatting}。自定义需求：{custom_requirements}。",
        "append_disclaimer": False
    }
]

async def init_and_seed_db():
    """初始化数据库并注入基础赛道、模板与Prompt资产"""
    if "sqlite" in settings.DATABASE_URL:
        db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 1. 检查赛道是否已存在
        result = await session.execute(select(Category))
        existing_categories = result.scalars().all()
        if not existing_categories:
            print("[Seed] 正在初始化 11 大赛道数据...")
            for cat_data in CATEGORIES_DATA:
                cat = Category(
                    id=cat_data["id"],
                    name=cat_data["name"],
                    icon=cat_data["icon"],
                    sort_order=cat_data["sort_order"],
                    description=cat_data.get("description")
                )
                session.add(cat)
            await session.commit()
            print("[Seed] 赛道数据初始化完成！")

        # 2. 检查模板与提示词是否已存在
        result = await session.execute(select(Template))
        existing_templates = result.scalars().all()
        if not existing_templates:
            print("[Seed] 正在初始化模板与 Prompt 资产...")
            for tpl_data in TEMPLATES_DATA:
                tpl = Template(
                    id=tpl_data["id"],
                    category_id=tpl_data["category_id"],
                    name=tpl_data["name"],
                    tag=tpl_data["tag"],
                    sort_order=tpl_data["sort_order"],
                    description=tpl_data.get("description")
                )
                session.add(tpl)
                
                # 为该模板注入大纲 Prompt
                prompt_outline = PromptConfig(
                    template_id=tpl_data["id"],
                    prompt_type="outline",
                    system_prompt=tpl_data["outline_system"],
                    user_prompt_template=tpl_data["outline_user"],
                    model_name="deepseek-chat",
                    temperature=0.7,
                    version=1,
                    is_active=True,
                    append_disclaimer=tpl_data.get("append_disclaimer", False),
                    disclaimer_text=TCM_DISCLAIMER if tpl_data.get("append_disclaimer") else None
                )
                session.add(prompt_outline)

                # 为该模板注入全文生成 Prompt
                prompt_article = PromptConfig(
                    template_id=tpl_data["id"],
                    prompt_type="article",
                    system_prompt=tpl_data["article_system"],
                    user_prompt_template=tpl_data["article_user"],
                    model_name="deepseek-chat",
                    temperature=0.6,
                    version=1,
                    is_active=True,
                    append_disclaimer=tpl_data.get("append_disclaimer", False),
                    disclaimer_text=TCM_DISCLAIMER if tpl_data.get("append_disclaimer") else None
                )
                session.add(prompt_article)

            await session.commit()
            print("[Seed] 模板及 Prompt 资产初始化完成！")

if __name__ == "__main__":
    asyncio.run(init_and_seed_db())
