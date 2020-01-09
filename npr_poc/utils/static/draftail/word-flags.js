const wordiness = {
    "absolutely essential": "essential",
    aforementioned: "delete,",
    "a bigger degree of": "more",
    "a greater degree of": "more",
    "a higher degree of": "more",
    "a larger degree of": "more",
    "a considerable amount of": "delete, or be specific",
    "a decreased number of": "fewer",
    "a distance of": "just state the distance",
    "a lesser degree of": "less",
    "a smaller degree of": "fewer",
    "a majority of": "most, much of, many",
    "a person who is": "a xxx person",
    "a total of": "just state the number",
    "added bonus": "bonus",
    "advance notice": "notice",
    "advance reservations": "reservations",
    "advance warning": "warning",
    "advance planning": "planning",
    "after all is said and done": "delete,",
    "along the lines of": "like",
    "any and all": "all",
    "are such that": "delete,",
    "is such that": "delete,",
    "are able to": "can, or delete",
    "was able to":
        'could, or remove and change the verb after "to" into past tense',
    "were able to":
        'could, or remove and change the verb after "to" into past tense',
    "armed gunman": "gunman",
    "assemble together": "assemble",
    "attach together": "attach",
    "as a matter of fact": "in fact or delete",
    "as a means to": "to",
    "as a result of": "because of",
    "as a whole": "delete,",
    "as a way to": "to",
    "as being a": "as or delete",
    "as it truly is": "delete,",
    "as of the moment": "delete,",
    "as the case may be": "delete,",
    "at a later date": "later",
    "at the conclusion of": "after",
    "at all times": "always or delete",
    "at first glance": "delete,",
    "at the present time": "currently, now",
    "at the same time that": "while",
    "at this point in time": "now or delete",
    "autobiography of his [or her] life": "autobiography",
    "bald-headed": "bald",
    "based in large part on": "based on",
    "based on the fact that": "since/because",
    "basic necessity": "necessity",
    "basic fundamentals": "basics or fundamentals",
    "because of the fact of": "because of",
    "being that": "because",
    "best ever": "best",
    "beyond a shadow of a doubt": "delete,",
    "blend together": "blend",
    "both of these": "both",
    "both of them": "both",
    "both of the": "both",
    "brings to mind": "recalls/suggests",
    "brief moment": "moment",
    "brief summary": "summary",
    "burning embers": "embers",
    "by and large": "delete,",
    "by definition": "delete,",
    "by leaps and bounds": "delete,",
    "by means of": "by",
    "by the same token": "delete, or similarly/likewise",
    "by the use of": "using",
    "came to a realization": "realized/recognized",
    "came to an abrupt end": "end[ed] abruptly",
    "careful scrutiny": "scrutiny",
    "can be seen as": "is or delete",
    "classify into groups": "classify",
    "clearly articulate": "articulate",
    "close scrutiny": "scrutiny",
    "close down": "close",
    "close up": "close",
    "collaborate together": "collaborate",
    "combine together": "combine",
    "come to the understanding": "understand",
    "common similarities": "similarities",
    "comparatively larger than": "larger than/smaller than",
    "comparatatively smaller than": "smaller than",
    "compare and contrast": "compare",
    "compete with each other": "compete",
    "complete stranger": "stranger",
    completely: "delete,",
    "concerning the matter of": "about/regarding",
    "conduct an investigation into": "investigate",
    "connected together": "connected",
    "continue into the future": "continue or delete",
    "continue on": "continue",
    "consensus of opinion": "consensus",
    "consider to be": "delete,",
    "considered to be": "delete,",
    "core essence": "delete,",
    "correctional facility": "jail",
    "crisis situation": "crisis",
    "dates back to": "dates to",
    "depreciate in value": "depreciate",
    "great pleasure from": "enjoy, appreciate, etc.",
    "despite the fact that": "although",
    "did not succeed": "failed",
    "disappear from sight": "disappear",
    "doomed to perish": "doomed",
    "due to the effects": "because",
    "due to the fact that": "because",
    "dull in appearance": "dull",
    "during the course of": "during, while",
    "each and every": "each, every",
    "each individual": "delete, or everyone",
    "early on in the": "early in the",
    "each separate incident": "each incident",
    "economically deprived": "poor",
    "eliminate altogether": "eliminate",
    "emergency situation": "emergency",
    "enclosed herewith": "enclosed",
    "end result": "result",
    "engaged in": "delete,",
    "enter into": "enter or delete",
    "epic quest": "quest or epic",
    "equal to one another": "equal",
    "equally as good": "equally good or equal",
    "erode away": "erode",
    "every single one": "each one, all, each",
    "exactly identical": "identical",
    "exactly the same": "the same for jack, every well was exactly the same",
    "fair amount": "delete, [or be specific]",
    "fall down": "fall",
    "few and far between": "rare, unusual or delete",
    "few in number": "few",
    "filled to capacity": "filled [full]",
    "final outcome": "final or delete",
    "first priority": "priority",
    "first and foremost": "first",
    "fly through the air": "fly",
    "foreign imports": "imports",
    "for all intents and purposes": "delete,",
    "for that which is": "for the",
    "for the manner in which": "the way",
    "for the purpose of": "to, for",
    "foreseeable future": "[when exactly?]",
    "free gift": "gift",
    "frozen ice": "ice",
    "future plans": "plans or prospects",
    "gain entry into": "enter",
    "general consensus": "consensus",
    "general public": "public",
    "give an indication of": "indicate",
    "give consideration to": "consider",
    "grave crisis": "crisis",
    "grow in size": "grow",
    "hand in hand": "together",
    "has the ability to": "can",
    "a tendency to": "often or delete",
    "been found to be": "is/was/are",
    "the ability to": "can/could",
    "the capacity for": "can/could",
    "the effect of": "delete,",
    "the opportunity to": "can/could",
    "an effect upon": "influenced",
    "hear the sound of": "hear",
    "heat up": "heat",
    "I myself": "i",
    "clear and concise": "[concisely] concise",
    "a situation in which": "eperienced",
    "in a very real sense": "delete,",
    "in a way that is clear": "clearly or clear way",
    "in actuality": "delete,",
    "in all probability": "probably/likely",
    "in close proximity": "near",
    "in light of the fact that": "because",
    // Example of bad copy / trigger words
    "the right direction": "",
    "eye candy": "",
    "mind over matter": "",
    "absolutely crackers": "",
    "hand in hand": "",
    "welcome home": "",
    "happy hours": "",
    "young parents": "",
    "mental illness": "",
};

const unusalWords = {
    "means-tested benefits": "",
    "carers allowance": "",
    "non-means tested benefits": "",
    "contributory benefits": ""
};

const flagKeys = [...Object.keys(wordiness), ...Object.keys(unusalWords)];

const flagsRegexPattern = `(${flagKeys.join("|")})`;

const squigglyStyles = {
    textDecorationLine: "underline",
    textDecorationStyle: "wavy",
    textDecorationColor: "orange"
};

const Flag = ({ children }) =>
    React.createElement(
        "span",
        {
            style: squigglyStyles,
            "data-draftail-balloon": true,
            "aria-label": "This may be too wordy"
        },
        children
    );

class WordFlags {
    constructor() {
        this.component = Flag;
        this.strategy = this.getDecorations.bind(this);
    }

    getDecorations(block, callback) {
        if (block.getType() === "atomic") {
            return;
        }

        const blockText = block.getText();

        for (const flag of blockText.matchAll(
            new RegExp(flagsRegexPattern, "g")
        )) {
            callback(flag.index, flag.index + flag[0].length);
        }
    }
}

window.draftail.registerDecorator(new WordFlags());
