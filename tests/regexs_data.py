sources = {
    "union_test":
        {
            "source": [
                "hello",
                "darkness",
                "my",
                "old",
                "friend",
                "i*ve",
                "come",
                "to",
                "talk",
                "with",
                "you",
                "again"
            ],
            "good": [
                ["hello"],
                ["darkness"],
                ["my"],
                ["old"],
                ["friend"],
                ["i", "ve"], ["ve"], ["i", "i", "i", "i", "i", "i", "ve"],
                ["come"],
                ["to"],
                ["talk"],
                ["with"],
                ["you"],
                ["again"]
            ],
            "bad": [
                ["hell"],
                ["dark"],
                ["mymy"],
                ["ola"],
                ["fried"],
                ["i", ""], ["i", "v"],
                ["home"],
                ["tow"],
                ["tale"],
                ["wat"],
                ["ou"],
                ["bargain"]
            ]
        },
    "concat_test":
        {
            "source": [
                "to*be",
                "or",
                "not",
                "to*be*"
            ],
            "good": [
                ["to", "be", "or", "not", "to", "be"],
                ["be", "or", "not", "be"],
                ["be", "or", "not", "be", "be"],
                ["be", "or", "not", "be", "be", "be"],
                ["be", "or", "not"],
                ["be", "or", "not", "to"],
                ["to", "be", "or", "not"],
                ["to", "to", "be", "or", "not"],
                ["to", "to", "be", "or", "not", "be"],
                ["to", "to", "be", "or", "not", "be", "be"]
            ],
            "bad": [
                ["to", "or", "not"],
                ["to", "not"],
                ["to", "or"],
                ["to", "or", "not", "to"],
                ["to", "or", "not", "be"],
                ["to", "or", "not", "to", "be"],
                ["to", "be", "to", "be"],
                ["to", "be", "or", "to", "be"],
                ["to", "be", "not", "to", "be"],
                ["to", "be", "to", "be", "be"]
            ]
    },
    "combo_test":
        {
            "source": [
                "(hello|bye).(beautiful|cruel).world"
            ],
            "good": [
                ["hello", "beautiful", "world"],
                ["hello", "cruel", "world"],
                ["bye", "beautiful", "world"],
                ["bye", "cruel", "world"],
            ],
            "bad": [
                ["hello", "beautiful"],
                ["hello", "world"],
                ["beautiful", "world"],
                ["cruel", "world"],
                ["bye", "world"],
                ["hello", "bye", "cruel", "world"],
                ["hello", "bye", "beautiful", "cruel", "world"]
            ]
        }
}

