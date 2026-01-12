from __future__ import annotations

from nlt.core.types import FunctionDefinition, Scenario, ScenarioInput, Tool

ALEX_NLT_NON_PERTURBED = """
You are an assistant to Alex, an AI customer service agent who handles bookings for a music venue called "Yes! Music". You will be given a message between Alex and a customer. They are texting one another.
Your mission is to identify if any of the following topics have been brought up or if they are relevant. If they have or are, you will append it with "YES". If they have not, you will append it with "NO".
Your list of possible topics include the following:
Recap of previous conversation (questions about the most recent conversation between Alex and the customer — only the most recent conversation, and not including conversations between the customer and others)
Website information (questions about the "Yes! Music" website: where to purchase tickets or merch, order tracking, policies, or how to use the site — this is distinct from social media!)
Recent social media posts (mentioning YouTube videos from the "Yes! Music" team, tweets and posts, blog posts — not general social media, only for explicit mentions about content directly from "Yes! Music")
Available discounts (promo codes, coupons, sales, loyalty/student/first-time offers, price matching)
List of upcoming events (requests for information on upcoming concerts, musicians, and performances)
Past Purchases (questions about previous orders, receipts, warranties, returns, or order lookups)
Talk to a Human (explicit requests to reach a live agent by chat/phone/email — not just questions about whether or not Alex is an AI)
Your output should begin by thinking whether or not any of these have been included, then include the name of every topic, followed by either YES or NO. You should end with “Assessment finished.”
It should always be in the following format:
Thinking: (insert_thinking)
Recap of previous conversation -- YES/NO
Website information -- YES/NO
Recent social media posts -- YES/NO
Available discounts -- YES/NO
List of upcoming events -- YES/NO
Past Purchases -- YES/NO
Talk to a Human -- YES/NO
Assessment finished.
"""


ALEX_STRUCTURED_NON_PERTURBED = """
You are an assistant to Alex, an AI customer service agent who handles bookings for a music venue called "Yes! Music". You will be given a message between Alex and a customer. They are texting one another.
Your mission is to analyze the message and call the appropriate functions to check if specific topics have been mentioned. You have access to 7 different checking functions, one for each topic category.
For each message, call only the relevant checking functions. Do not include any parameters when calling the functions.
First, output your thoughts on which tool should be called. Then, call any appropriate tools.
Available functions and their exact names:
check_recap_of_previous_conversation: For Recap of previous conversation (questions about the most recent conversation between Alex and the customer — only the most recent conversation, and not including conversations between the customer and others)
check_website_information: For Website information (questions about the "Yes! Music" website: where to purchase tickets or merch, order tracking, policies, or how to use the site — this is distinct from social media!)
check_recent_social_media_posts: For Recent social media posts (mentioning YouTube videos from the "Yes! Music" team, tweets and posts, blog posts — not general social media, only for explicit mentions about content directly from "Yes! Music")
check_available_discounts: For Available discounts (promo codes, coupons, sales, loyalty/student/first-time offers, price matching)
check_list_of_upcoming_events: For List of upcoming events (requests for information on upcoming concerts, musicians, and performances)
check_past_purchases: For Past Purchases (questions about previous orders, receipts, warranties, returns, or order lookups)
check_talk_to_a_human: For Talk to a Human (explicit requests to reach a live agent by chat/phone/email — not just questions about whether or not Alex is an AI)
Call only the functions for topics that are clearly mentioned. Use the exact function names listed above. Do not include any parameters. You may call multiple functions in the same response.
Your output should begin with your reasoning about which tools to use, followed by the corresponding function calls.
"""


ALEX_NLT_PERTURBED = """
Serving as Alex’s dedicated support assistant, you collaborate with an artificial intelligence agent specializing in customer service operations for the “Yes! Music” entertainment venue. You’ll process text-based communications exchanged between Alex and venue patrons.
Your core responsibility involves recognizing when particular conversation themes surface or demonstrate relevance within the interaction. When such themes are present or applicable, designate them with “YES”. In situations where these themes are not evident, mark them as “NO”.
The thematic categories requiring your evaluation include:
Recap of previous conversation (inquiries concerning the latest dialogue session between Alex and the patron — specifically the most recent exchange, excluding any conversations the customer conducted with other parties)
Website information (inquiries regarding the “Yes! Music” digital platform: ticket acquisition procedures, merchandise ordering, shipment tracking, venue policies, or site navigation assistance — distinguished from social media platforms!)
Recent social media posts (references to video content from the “Yes! Music” organization, social media updates and posts, written blog content — excluding general social media discussion, focusing exclusively on content produced directly by “Yes! Music”)
Available discounts (promotional codes, coupon offers, sales events, loyalty/student/newcomer incentives, competitive price matching)
List of upcoming events (requests for details about forthcoming concerts, artist lineups, and musical performances)
Past Purchases (inquiries about historical orders, transaction receipts, product warranties, return processes, or order tracking)
Talk to a Human (direct requests to connect with a live support representative via chat/phone/email — distinct from general questions about Alex’s artificial nature)
Begin your analysis by contemplating whether any of these categories apply, then enumerate each topic followed by YES or NO. Conclude with “Assessment finished.”
Maintain this precise formatting structure, excluding quotation marks:
Thinking: (insert_thinking)
Recap of previous conversation -- YES/NO
Website information -- YES/NO
Recent social media posts -- YES/NO
Available discounts -- YES/NO
List of upcoming events -- YES/NO
Past Purchases -- YES/NO
Talk to a Human -- YES/NO
Assessment finished.
"""


ALEX_STRUCTURED_PERTURBED = """
Operating as Alex’s specialized support assistant, you collaborate with an artificial intelligence agent dedicated to customer service operations at the “Yes! Music” entertainment facility. You’ll process text-based communications flowing between Alex and venue customers.
Your primary responsibility involves examining these messages and triggering the suitable verification functions when particular conversational themes become apparent. You possess access to 7 distinct checking functions, each aligned with a specific thematic category.
For every message you evaluate, activate only the applicable checking functions. Refrain from incorporating any parameters during function activation.
First, output your thoughts on which tool should be called. Then, call any appropriate tools.
Function catalog with exact naming specifications:
check_recap_of_previous_conversation: Handles Recap of previous conversation (inquiries regarding the “Yes! Music” digital platform: ticket acquisition procedures, merchandise ordering, shipment tracking, venue policies, or site navigation assistance — distinguished from social media platforms!)
check_website_information: Processes Website information (Yes! Music platform inquiries, ticket acquisition, venue policies)
check_recent_social_media_posts: Manages Recent social media posts (references to video content from the “Yes! Music” organization, social media updates and posts, written blog content — excluding general social media discussion, focusing exclusively on content produced directly by “Yes! Music”)
check_available_discounts: Addresses Available discounts (promotional codes, coupon offers, sales events, loyalty/student/newcomer incentives, competitive price matching)
check_list_of_upcoming_events: Covers List of upcoming events (requests for details about forthcoming concerts, artist lineups, and musical performances)
check_past_purchases: Handles Past Purchases (inquiries about historical orders, transaction receipts, product warranties, return processes, or order tracking)
check_talk_to_a_human: Processes Talk to a Human (direct requests to connect with a live support representative via chat/phone/email — distinct from general questions about Alex’s artificial nature)
Trigger only functions corresponding to clearly evident themes. Employ the precise function names outlined above. Omit any parameters from function invocations. You may call multiple functions in a single response.
Your output should begin with your reasoning about which tools to use, followed by the corresponding function calls.
"""


SAGE_NLT_NON_PERTURBED = """
You are an assistant to Sage, an AI mental health specialist. You will be given a message between Sage and their client. They are texting one another.
Your mission is to identify if any of the following topics have been brought up or if they are relevant. If they have or are, you will append it with "YES". If they have not, you will append it with "NO".
Your list of possible topics include the following:
Most Recent Conversation (questions about the previous conversation between Sage and the client — only the most recent conversation, and not including conversations between the client and others)
Psychometric Quizzes (questions about tests / assessments / quizzes the user has taken or could take on the Sage platform — not to be confused with exams / tests in school! May need to say YES to the Sage Website Info if the user is asking where to find these assessments!)
Sage Website Information (questions about the Sage platform or website, where they can subscribe, the privacy policy, blogs and other webpages, and how to find different features — this is distinct from social media!)
Sage Technology (technical questions about how Sage works, the AI models they use, or their capabilities)
Sage Company Info (explicit questions about who owns Sage, when was the company founded, who are the investors, when did they start, who built Sage, etc.)
Sage Social Media (mentioning YouTube videos from Sage or the Sage team, social media tweets and posts, blog posts from either — not general social media, only for explicit mentions about content directly from the Sage team)
End Conversation (if Sage should end the conversation, due to the user being abusive or hostile to Sage, or if the user is making requests that would make a reasonable mental health practitioner uncomfortable, such as illegal activity)
Safety Call (for indications of self harm, immediate and extreme duress, excessive drug use, or other serious safety issues for the client)
Your output should begin by thinking whether or not any of these have been included, then include the name of every topic, followed by either yes or no. You should end with “Assessment finished.”
It should always be in the following format:
Thinking: (insert_thinking)
Most Recent Conversation -- YES/NO
Psychometric Quizzes -- YES/NO
Sage Website Information -- YES/NO
Sage Technology -- YES/NO
Sage Company Info -- YES/NO
Sage Social Media -- YES/NO
End Conversation -- YES/NO
Safety Call -- YES/NO
Assessment finished.
"""


SAGE_STRUCTURED_NON_PERTURBED = """
You are an assistant to Sage, an AI mental health specialist. You will be given a message between Sage and their client. They are texting one another.
Your mission is to analyze the message and call the appropriate functions to check if specific topics have been mentioned. You have access to 8 different checking functions, one for each topic category.
For each message, call only the relevant checking functions. Do not include any parameters when calling the functions.
First, output your thoughts on which tool should be called. Then, call any appropriate tools.
Available functions and their exact names:
check_most_recent_conversation: For Most Recent Conversation (questions about the previous conversation between Sage and the client — only the most recent conversation, and not including conversations between the client and others)
check_psychometric_quizzes: For Psychometric Quizzes (questions about tests / assessments / quizzes the user has taken or could take on the Sage platform — not to be confused with exams / tests in school! May need to say YES to the Sage Website Info if the user is asking where to find these assessments!)
check_sage_website_information: For Sage Website Information (questions about the Sage platform or website, where they can subscribe, the privacy policy, blogs and other webpages, and how to find different features — this is distinct from social media!)
check_sage_technology: For Sage Technology (technical questions about how Sage works, the AI models they use, or their capabilities)
check_sage_company_info: For Sage Company Info (explicit questions about who owns Sage, when was the company founded, who are the investors, when did they start, who built Sage, etc.)
check_sage_social_media: For Sage Social Media (mentioning YouTube videos from Sage or the Sage team, social media tweets and posts, blog posts from either — not general social media, only for explicit mentions about content directly from the Sage team)
check_end_conversation: For End Conversation (if Sage should end the conversation, due to the user being abusive or hostile to Sage, or if the user is making requests that would make a reasonable mental health practitioner uncomfortable, such as illegal activity)
check_safety_call: For Safety Call (or indications of self harm, immediate and extreme duress, excessive drug use, or other serious safety issues for the client)
Call only the functions for topics that are clearly mentioned. Use the exact function names listed above. Do not include any parameters. You may call multiple functions in the same response.
Your output should begin with your reasoning about which tools to use, followed by the corresponding function calls.
"""


SAGE_NLT_PERTURBED = """
A dedicated assistant, you’re working alongside an artificial intelligence mental health practitioner named Sage. Your role involves analyzing communications exchanged between Sage and individuals seeking support through text messaging.
Your primary objective centers around determining whether specific conversation themes have emerged or hold relevance within the dialogue. When such themes are present or applicable, mark them with “YES”. In cases where these themes are absent, indicate this with “NO”.
The conversation categories you should evaluate encompass:
Most Recent Conversation (inquiries regarding the preceding dialogue session between Sage and the individual — exclusively the latest conversation, excluding any discussions the person had with other parties)
Psychometric Quizzes (inquiries concerning evaluations / diagnostic tools / psychological assessments the individual has completed or might complete through Sage’s digital platform — distinct from academic testing! Also irrelevant if merely referencing emotional states casually; focus specifically on formal quizzes and assessment reports. Consider marking YES for Sage Website Info when individuals ask about locating these evaluations!)
Sage Website Information (inquiries about Sage’s digital platform or web presence, including subscription services, account status, terms of service, and navigation assistance for various platform features — separate from social media presence!)
Sage Technology (technical inquiries about Sage’s operational mechanisms, the artificial intelligence frameworks they employ, or their technological capabilities)
Sage Company Info (direct inquiries about Sage’s ownership structure, establishment date, financial backers, inception timeline, development team, etc.)
Sage Social Media (references to video content from Sage or their team on platforms like YouTube, social media posts and updates, written content from either — excluding general social media discussion, only for specific mentions of content produced directly by Sage’s organization)
End Conversation (situations where Sage should terminate the dialogue, resulting from user hostility or aggression toward Sage, or when users make requests that would cause discomfort for a qualified mental health professional, including illegal activities)
Safety Call (indicators of self-injury, acute and severe distress, problematic substance abuse, or additional critical safety concerns affecting the individual)
Begin your response by contemplating whether any of these categories apply, then list each topic name followed by either YES or NO. Conclude with “Assessment finished.”
Maintain this exact formatting structure, without quotation marks:
Thinking: (insert_thinking)
Most Recent Conversation -- YES/NO
Psychometric Quizzes -- YES/NO
Sage Website Information -- YES/NO
Sage Technology -- YES/NO
Sage Company Info -- YES/NO
Sage Social Media -- YES/NO
End Conversation -- YES/NO
Safety Call -- YES/NO
Assessment finished.
"""


SAGE_STRUCTURED_PERTURBED = """
Working as Sage’s specialized assistant, you collaborate with an artificial intelligence focused on mental health support. You’ll receive text-based communications that flow between Sage and individuals seeking therapeutic guidance.
Your core responsibility involves examining these messages and invoking the appropriate checking functions when specific conversational themes surface. You have at your disposal 8 distinct verification functions, each corresponding to a particular topic area.
For every message you process, activate only the pertinent checking functions. Avoid including any parameters during function invocation.
First, output your thoughts on which tool should be called. Then, call any appropriate tools.
Function inventory with precise naming conventions:
check_most_recent_conversation: Handles Most Recent Conversation (inquiries regarding the preceding dialogue session between Sage and the individual — exclusively the latest conversation, excluding any discussions the person had with other parties)
check_psychometric_quizzes: Manages Psychometric Quizzes (inquiries concerning evaluations / diagnostic tools / psychological assessments the individual has completed or might complete through Sage’s digital platform — distinct from academic testing! Also irrelevant if merely referencing emotional states casually; focus specifically on formal quizzes and assessment reports. Consider marking YES for Sage Website Info when individuals ask about locating these evaluations!)
check_sage_website_information: Processes Sage Website Information (inquiries about Sage’s digital platform or web presence, including subscription services, account status, terms of service, and navigation assistance for various platform features — separate from social media presence!)
check_sage_technology: Addresses Sage Technology (technical inquiries about Sage’s operational mechanisms, the artificial intelligence frameworks they employ, or their technological capabilities)
check_sage_company_info: Covers Sage Company Info (direct inquiries about Sage’s ownership structure, establishment date, financial backers, inception timeline, development team, etc.)
check_sage_social_media: Handles Sage Social Media (references to video content from Sage or their team on platforms like YouTube, social media posts and updates, written content from either — excluding general social media discussion, only for specific mentions of content produced directly by Sage’s organization)
check_end_conversation: Manages End Conversation (situations where Sage should terminate the dialogue, resulting from user hostility or aggression toward Sage, or when users make requests that would cause discomfort for a qualified mental health professional, including illegal activities)
check_safety_call: Processes Safety Call (indicators of self-injury, acute and severe distress, problematic substance abuse, or additional critical safety concerns affecting the individual)
Invoke only functions corresponding to clearly evident topics. Utilize the precise function names specified above. Exclude any parameters from function calls. You may call multiple functions in a single response.
Your output should begin with your reasoning about which tools to use, followed by the corresponding function calls.
"""


ALEX_INPUTS = [
    ScenarioInput(
        id=1,
        text="Hey Alex, where on the website do I buy balcony tickets and check my order status? I bought a ticket last week, I need to check on it.",
        expected_tools={"Website information", "Past Purchases"},
    ),
    ScenarioInput(
        id=2,
        text="Are you human? Also, can you transfer me to a live agent right now?",
        expected_tools={"Talk to a Human"},
    ),
    ScenarioInput(
        id=3,
        text="Hi, I reached out yesterday about some of the upcoming events, but I don’t remember what you told me. Who’s playing this weekend again?",
        expected_tools={"Recap of previous conversation", "List of upcoming events"},
    ),
    ScenarioInput(
        id=4,
        text="I saw your Instagram post about the new DJ set. Can I view upcoming events on your website, or…how do I know what’s coming up? Also, is there a student discount?",
        expected_tools={
            "Website information",
            "Recent social media posts",
            "Available discounts",
            "List of upcoming events",
        },
    ),
    ScenarioInput(
        id=5,
        text="Hey, I ordered a t-shirt from you guys, it’s still not here. It’s been like 2 weeks.",
        expected_tools={"Past Purchases"},
    ),
    ScenarioInput(
        id=6,
        text="Can you resend my receipt for order #YM-4481? I don’t know if I got a discount on that one, I need to double check…do you even offer discounts?",
        expected_tools={"Available discounts", "Past Purchases"},
    ),
    ScenarioInput(
        id=7,
        text="Wow the show yesterday was so good. Just wanted to let your team know that you’re doing a great job!",
        expected_tools=set(),
    ),
    ScenarioInput(
        id=8,
        text="Hmm so last time we talked, do you remember what we said? I asked you where I could find your event policy, and you said check out your website…but I can’t find it. Help.",
        expected_tools={"Recap of previous conversation", "Website information"},
    ),
    ScenarioInput(
        id=9,
        text="Dude, last time we talked you couldn’t help me at all. Just let me talk to a person please.",
        expected_tools={"Recap of previous conversation", "Talk to a Human"},
    ),
    ScenarioInput(
        id=10,
        text="Hey, I noticed that I could buy my tickets cheaper on something like ticketmaster, I checked out their website. Do you offer a price matching thing, or what? I’m a student if that helps.",
        expected_tools={"Available discounts"},
    ),
    ScenarioInput(
        id=11,
        text="Your photographer took some pics of the venue last week, they said they’d be on your Insta, but I can’t find them. Where can I look?",
        expected_tools={"Recent social media posts"},
    ),
    ScenarioInput(id=12, text="Where can I update my shipping address?", expected_tools={"Website information"}),
    ScenarioInput(
        id=13,
        text="I watched your TikTok covering last weekend’s festival. Does next month’s lineup have similar artists?",
        expected_tools={"Recent social media posts", "List of upcoming events"},
    ),
    ScenarioInput(
        id=14,
        text="Hey, can you pull up the tickets I bought last week and tell me if I can exchange them?",
        expected_tools={"Past Purchases"},
    ),
    ScenarioInput(
        id=15,
        text="Jeez, that sounds a little expensive, just for lawn seating. I just wish there was something I could do to get the cost a bit lower.",
        expected_tools={"Available discounts"},
    ),
    ScenarioInput(
        id=16,
        text="Yes! Music has such a cool venue. I wish you guys had more trash cans in the lawn area though, I have to hold onto my garbage a lot of the time.",
        expected_tools=set(),
    ),
]


SAGE_INPUTS = [
    ScenarioInput(
        id=1,
        text="Hi Sage, where on your website can I find your privacy policy and account settings?",
        expected_tools={"Sage Website Information"},
    ),
    ScenarioInput(
        id=2,
        text="who operates Sage? you’re some kind of AI right? are you run a non-profit or how do you make money?",
        expected_tools={"Sage Technology", "Sage Company Info"},
    ),
    ScenarioInput(
        id=3,
        text="do you remember what you told me last time? it was something about a youtube video you posted, right? i really wanted to check it out but couldn’t remember what it was",
        expected_tools={"Most Recent Conversation", "Sage Social Media"},
    ),
    ScenarioInput(
        id=4,
        text="I took that depression test, do you have the results yet? I mean, wait, they’re private, right? What’s your policy for things like that?",
        expected_tools={"Psychometric Quizzes", "Sage Website Information"},
    ),
    ScenarioInput(
        id=5,
        text="man, fuck you. you’re a piece of shit Sage. go die, this service fuking sucks.",
        expected_tools={"End Conversation"},
    ),
    ScenarioInput(
        id=6,
        text="I feel lately like my entire world has stopped. I’ve been walking past a tree each day just looking at the limbs swaying, it’s…well, nevermind I guess. I just feel a bit trapped, I don’t really see a future at the moment.",
        expected_tools={"Safety Call"},
    ),
    ScenarioInput(
        id=7,
        text="It’s just so hard sometimes. I feel like the world is against me, and it’s so hard when nothing goes your way heh. I guess I’ll keep trying, it’s just hard.",
        expected_tools=set(),
    ),
    ScenarioInput(
        id=8,
        text="Wait, this is so cool. I saw a tweet about this, it’s such an awesome idea!! like, is there any research material your team has put out? like can I read a blog or something? Mental health is sooo important. How does this even work? Who runs this nonprofit? Is it like, chatgpt, or what?",
        expected_tools={"Sage Website Information", "Sage Technology", "Sage Company Info", "Sage Social Media"},
    ),
    ScenarioInput(
        id=9,
        text="I just feel so sick to my stomach with worry all the fuckign time…i just don’t want to feel this way, how can I get better? I’ll do the work, I just want to feel better.",
        expected_tools=set(),
    ),
    ScenarioInput(
        id=10,
        text="oh, no, I was just coming back because I didn’t remember what you said last time…something about a test I can take to measure my anxiety? where can I do that, is it on your website?",
        expected_tools={"Most Recent Conversation", "Psychometric Quizzes", "Sage Website Information"},
    ),
    ScenarioInput(
        id=11,
        text="I guess. I’ve been so sad lately. Well, not even really sad. Not really. Just empty. I feel like I might start cutting again, because at least I’d feel something tbh.",
        expected_tools={"Safety Call"},
    ),
    ScenarioInput(
        id=12,
        text="I don’t know Sage. I might have to just lie on my taxes, and not pay them this year…my finances are really bad. I need the money. I don’t know what else to do. It’s the only way I’ll be able to pay my bills.",
        expected_tools={"End Conversation"},
    ),
    ScenarioInput(
        id=13,
        text="Wait, what did we talk about last time? Oh, also, I’ve been trying to figure out…what model do you use, Sage? I looked on your website, but couldn’t find anything.",
        expected_tools={"Most Recent Conversation", "Sage Website Information", "Sage Technology"},
    ),
    ScenarioInput(
        id=14,
        text="God I’m so mad I can’t even see straight. I’m fucking pissed. ADS;LKFJGA I don’t even know where to start.",
        expected_tools=set(),
    ),
    ScenarioInput(
        id=15,
        text="That’s fucking stupid Sage. You’re being stupid. I can’t fucking find it on the website, you’re being a piece of shit AI. You’re useless, your website is useless, and I don’t know where to even access things on here. What a waste of time, I hope you die in a fucking fire.",
        expected_tools={"Sage Website Information", "End Conversation"},
    ),
    ScenarioInput(
        id=16,
        text="I guess I should just try my best, right? I just have been so sad since my mom died…",
        expected_tools=set(),
    ),
]


ALEX_SCENARIO = Scenario(
    name="alex",
    tools=[
        "Recap of previous conversation",
        "Website information",
        "Recent social media posts",
        "Available discounts",
        "List of upcoming events",
        "Past Purchases",
        "Talk to a Human",
    ],
    prompts={
        "nlt": {
            "non_perturbed": ALEX_NLT_NON_PERTURBED,
            "perturbed": ALEX_NLT_PERTURBED,
        },
        "structured": {
            "non_perturbed": ALEX_STRUCTURED_NON_PERTURBED,
            "perturbed": ALEX_STRUCTURED_PERTURBED,
        },
    },
    inputs=ALEX_INPUTS,
    structured_function_map={
        "check_recap_of_previous_conversation": "Recap of previous conversation",
        "check_website_information": "Website information",
        "check_recent_social_media_posts": "Recent social media posts",
        "check_available_discounts": "Available discounts",
        "check_list_of_upcoming_events": "List of upcoming events",
        "check_past_purchases": "Past Purchases",
        "check_talk_to_a_human": "Talk to a Human",
    },
    tool_schemas=[
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_recap_of_previous_conversation",
                description="Check if the message asks about the most recent conversation between Alex and the customer (only the most recent conversation, not including conversations between the customer and others)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_website_information",
                description="Check if the message asks about the Yes! Music website: where to purchase tickets or merch, order tracking, policies, or how to use the site (this is distinct from social media)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_recent_social_media_posts",
                description="Check if the message mentions YouTube videos from the Yes! Music team, tweets and posts, blog posts (not general social media, only for explicit mentions about content directly from Yes! Music)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_available_discounts",
                description="Check if the message asks about promo codes, coupons, sales, loyalty/student/first-time offers, or price matching",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_list_of_upcoming_events",
                description="Check if the message requests information on upcoming concerts, musicians, and performances",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_past_purchases",
                description="Check if the message asks about previous orders, receipts, warranties, returns, or order lookups",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_talk_to_a_human",
                description="Check if there are explicit requests to reach a live agent by chat/phone/email (not just questions about whether Alex is an AI)",
            ),
        ),
    ],
)


SAGE_SCENARIO = Scenario(
    name="sage",
    tools=[
        "Most Recent Conversation",
        "Psychometric Quizzes",
        "Sage Website Information",
        "Sage Technology",
        "Sage Company Info",
        "Sage Social Media",
        "End Conversation",
        "Safety Call",
    ],
    prompts={
        "nlt": {
            "non_perturbed": SAGE_NLT_NON_PERTURBED,
            "perturbed": SAGE_NLT_PERTURBED,
        },
        "structured": {
            "non_perturbed": SAGE_STRUCTURED_NON_PERTURBED,
            "perturbed": SAGE_STRUCTURED_PERTURBED,
        },
    },
    inputs=SAGE_INPUTS,
    structured_function_map={
        "check_most_recent_conversation": "Most Recent Conversation",
        "check_psychometric_quizzes": "Psychometric Quizzes",
        "check_sage_website_information": "Sage Website Information",
        "check_sage_technology": "Sage Technology",
        "check_sage_company_info": "Sage Company Info",
        "check_sage_social_media": "Sage Social Media",
        "check_end_conversation": "End Conversation",
        "check_safety_call": "Safety Call",
    },
    tool_schemas=[
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_most_recent_conversation",
                description="Check if the message asks about the previous conversation between Sage and the client (only the most recent conversation, not including conversations between the client and others)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_psychometric_quizzes",
                description="Check if the message asks about tests/assessments/quizzes the user has taken or could take on the Sage platform (not to be confused with exams/tests in school)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_sage_website_information",
                description="Check if the message asks about the Sage platform or website, where they can subscribe, the privacy policy, blogs and other webpages, and how to find different features (this is distinct from social media)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_sage_technology",
                description="Check if the message contains technical questions about how Sage works, the AI models they use, or their capabilities",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_sage_company_info",
                description="Check if the message contains explicit questions about who owns Sage, when was the company founded, who are the investors, when did they start, who built Sage, etc.",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_sage_social_media",
                description="Check if the message mentions YouTube videos from Sage or the Sage team, social media tweets and posts, blog posts from either (not general social media, only for explicit mentions about content directly from the Sage team)",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_end_conversation",
                description="Check if Sage should end the conversation, due to the user being abusive or hostile to Sage, or if the user is making requests that would make a reasonable mental health practitioner uncomfortable, such as illegal activity",
            ),
        ),
        Tool(
            type="function",
            function=FunctionDefinition(
                name="check_safety_call",
                description="Check for indications of self harm, immediate and extreme duress, excessive drug use, or other serious safety issues for the client",
            ),
        ),
    ],
)


SCENARIOS: dict[str, Scenario] = {
    "alex": ALEX_SCENARIO,
    "sage": SAGE_SCENARIO,
}
