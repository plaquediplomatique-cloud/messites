// Package keywords provides large, categorized English keyword lists used to
// generate domain-name candidates, plus generic prefixes/suffixes that are
// combined with them.
package keywords

// Category is a named group of related English keywords.
type Category struct {
	Name  string
	Words []string
}

// Categories holds every keyword category available for generation.
var Categories = []Category{
	{"music", []string{
		"music", "sound", "audio", "song", "tune", "melody", "beat", "rhythm",
		"band", "orchestra", "choir", "vocal", "singer", "songwriter", "lyric",
		"studio", "record", "vinyl", "album", "track", "mixtape", "remix",
		"instrument", "guitar", "bass", "drum", "piano", "keyboard", "violin",
		"cello", "flute", "trumpet", "saxophone", "synth", "amp", "speaker",
		"headphone", "playlist", "festival", "concert", "gig", "tour", "stage",
		"dj", "producer", "label", "indie", "acoustic", "podcast", "radio",
	}},
	{"rock", []string{
		"rock", "metal", "punk", "grunge", "alternative", "hardcore", "riff",
		"guitarist", "drummer", "moshpit", "amplifier", "distortion", "power",
		"chord", "solo", "anthem", "rebel", "leather", "skull", "thunder",
		"lightning", "blackmetal", "heavy", "garage", "vintage", "vinyl",
	}},
	{"cook", []string{
		"cook", "chef", "kitchen", "recipe", "bake", "bakery", "grill",
		"roast", "fry", "boil", "steam", "spice", "herb", "sauce", "broth",
		"soup", "stew", "salad", "dessert", "pastry", "bread", "cake", "pie",
		"cookie", "gourmet", "culinary", "cuisine", "pot", "pan", "knife",
		"oven", "stove", "blend", "whisk", "flavor", "taste", "meal", "dish",
		"platter", "menu", "brunch", "supper", "feast", "banquet", "catering",
	}},
	{"food", []string{
		"food", "eat", "snack", "diet", "nutrition", "organic", "vegan",
		"vegetarian", "protein", "carb", "grain", "fruit", "veggie",
		"seafood", "meat", "poultry", "dairy", "cheese", "milk", "egg",
		"honey", "sugar", "salt", "pepper", "oil", "butter", "coffee", "tea",
		"juice", "smoothie", "wine", "beer", "cocktail", "brew", "farmers",
		"harvest", "market", "grocery", "deli", "bistro", "diner", "pantry",
	}},
	{"travel", []string{
		"travel", "trip", "journey", "voyage", "tour", "vacation", "holiday",
		"explore", "adventure", "wander", "roam", "backpack", "hostel",
		"hotel", "resort", "cruise", "flight", "airline", "airport", "visa",
		"passport", "map", "guide", "destination", "island", "beach",
		"mountain", "desert", "jungle", "safari", "camp", "hike", "trail",
		"road", "trip", "nomad", "expedition", "sightseeing", "getaway",
	}},
	{"agency", []string{
		"agency", "consult", "consulting", "advisory", "bureau", "firm",
		"partner", "solution", "service", "group", "studio", "collective",
		"network", "team", "brand", "creative", "digital", "media", "press",
		"pr", "marketing", "ad", "campaign", "strategy", "growth", "talent",
		"staffing", "recruit", "outsource", "freelance", "consultant",
	}},
	{"tech", []string{
		"tech", "code", "dev", "software", "app", "cloud", "data", "byte",
		"pixel", "cyber", "digital", "robot", "ai", "machine", "network",
		"server", "database", "algorithm", "script", "compile", "debug",
		"stack", "framework", "platform", "gadget", "device", "sensor",
		"chip", "circuit", "startup", "saas", "api", "web", "internet",
	}},
	{"sport", []string{
		"sport", "fitness", "gym", "athlete", "coach", "training", "workout",
		"marathon", "race", "run", "jog", "swim", "cycle", "bike", "ski",
		"surf", "climb", "yoga", "pilates", "crossfit", "boxing", "wrestle",
		"soccer", "football", "basketball", "baseball", "tennis", "golf",
		"hockey", "rugby", "cricket", "volleyball", "skate", "team",
	}},
	{"fashion", []string{
		"fashion", "style", "trend", "wear", "outfit", "cloth", "apparel",
		"boutique", "designer", "model", "runway", "couture", "textile",
		"fabric", "denim", "shoe", "sneaker", "bag", "handbag", "jewelry",
		"watch", "accessory", "perfume", "cosmetic", "makeup", "beauty",
		"hair", "salon", "nail", "glam", "chic", "vogue", "wardrobe",
	}},
	{"finance", []string{
		"finance", "money", "bank", "invest", "capital", "fund", "asset",
		"wealth", "trade", "trading", "stock", "market", "equity", "credit",
		"loan", "mortgage", "insurance", "tax", "budget", "saving", "coin",
		"crypto", "bitcoin", "token", "ledger", "wallet", "broker", "advisor",
	}},
	{"health", []string{
		"health", "medical", "clinic", "hospital", "doctor", "nurse",
		"therapy", "wellness", "care", "pharma", "medicine", "dental",
		"vision", "surgery", "diagnosis", "patient", "vitamin", "supplement",
		"mental", "physio", "rehab", "cardio", "immune", "vaccine",
	}},
	{"home", []string{
		"home", "house", "garden", "lawn", "yard", "furniture", "decor",
		"interior", "renovation", "remodel", "build", "construction",
		"architect", "design", "kitchen", "bathroom", "bedroom", "living",
		"roof", "floor", "paint", "plumbing", "electric", "solar", "energy",
	}},
	{"pet", []string{
		"pet", "dog", "cat", "puppy", "kitten", "animal", "vet",
		"veterinary", "aquarium", "fish", "bird", "reptile", "groom",
		"leash", "collar", "kennel", "shelter", "rescue", "breed",
	}},
	{"kids", []string{
		"kid", "baby", "toddler", "child", "toy", "nursery", "school",
		"daycare", "parenting", "family", "playground", "game", "puzzle",
		"cartoon", "storybook", "lullaby",
	}},
	{"art", []string{
		"art", "paint", "draw", "sketch", "sculpt", "gallery", "museum",
		"canvas", "photo", "photography", "camera", "lens", "design",
		"illustration", "craft", "pottery", "ceramic", "mosaic", "graffiti",
	}},
	{"game", []string{
		"game", "gaming", "gamer", "console", "arcade", "esports", "puzzle",
		"board", "card", "dice", "quest", "level", "player", "avatar",
		"controller", "joystick", "stream", "twitch",
	}},
	{"nature", []string{
		"nature", "eco", "green", "forest", "wildlife", "ocean", "river",
		"lake", "planet", "earth", "climate", "solar", "wind", "recycle",
		"organic", "sustainable", "bloom", "flower", "plant", "tree",
	}},
	{"legal", []string{
		"legal", "law", "lawyer", "attorney", "court", "justice", "notary",
		"contract", "patent", "trademark", "compliance", "litigation",
	}},
	{"education", []string{
		"education", "academy", "school", "college", "university", "course",
		"class", "tutor", "learn", "teach", "study", "exam", "degree",
		"scholar", "campus", "curriculum", "lecture",
	}},
	{"realestate", []string{
		"realty", "estate", "property", "rent", "lease", "condo",
		"apartment", "mortgage", "broker", "landlord", "tenant", "housing",
	}},
	{"beauty", []string{
		"beauty", "spa", "skincare", "cosmetic", "glow", "facial", "massage",
		"relax", "aroma", "wellness", "lash", "brow", "tan",
	}},
	{"automotive", []string{
		"auto", "car", "motor", "vehicle", "garage", "mechanic", "tire",
		"engine", "drive", "race", "truck", "moto", "bike", "electric",
	}},
}

// Prefixes and Suffixes are short, brandable generic modifiers that get
// combined with keywords to expand the candidate space.
var Prefixes = []string{
	"my", "get", "the", "go", "try", "top", "best", "pro", "smart", "easy",
	"true", "real", "prime", "next", "new", "fresh", "urban", "modern",
	"pure", "meta", "hyper", "super",
}

var Suffixes = []string{
	"hub", "zone", "spot", "point", "base", "lab", "labs", "works", "co",
	"group", "team", "club", "house", "place", "city", "world", "land",
	"nation", "online", "digital", "web", "app", "io", "hq", "central",
	"now", "daily", "365", "pro", "plus", "verse", "ify", "ly", "kit",
}

// All returns every keyword across every category, flattened.
func All() []string {
	var out []string
	for _, c := range Categories {
		out = append(out, c.Words...)
	}
	return out
}
