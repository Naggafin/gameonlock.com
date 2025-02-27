# Generated by Django 5.1.4 on 2025-02-24 14:57

import auto_prefetch
import django.db.models.deletion
import django.db.models.manager
import djmoney.models.fields
import djmoney.models.validators
import djmoney.money
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
	initial = True

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="GoverningBody",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("icon", models.ImageField(blank=True, null=True, upload_to="")),
				("name", models.CharField(max_length=100, unique=True)),
				("description", models.TextField(blank=True, null=True)),
				(
					"type",
					models.CharField(
						choices=[
							("pro", "Professional"),
							("col", "Collegiate"),
							("ama", "Amateur"),
							("int", "International"),
							("clb", "Club"),
						],
						max_length=3,
						verbose_name="type of competition",
					),
				),
			],
			options={
				"verbose_name": "governing body",
				"verbose_name_plural": "governing bodies",
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="Player",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("icon", models.ImageField(blank=True, null=True, upload_to="")),
				("name", models.CharField(max_length=100)),
				("position", models.CharField(blank=True, max_length=100, null=True)),
				("jersey_number", models.PositiveIntegerField(blank=True, null=True)),
			],
			options={
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="Sport",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("icon", models.ImageField(null=True, upload_to="")),
				("name", models.CharField(max_length=100, unique=True)),
				("description", models.TextField(blank=True, null=True)),
				("slug_name", models.SlugField(blank=True, unique=True)),
			],
		),
		migrations.CreateModel(
			name="League",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("icon", models.ImageField(blank=True, null=True, upload_to="")),
				("name", models.CharField(max_length=100)),
				(
					"level_of_play",
					models.CharField(blank=True, max_length=100, null=True),
				),
				("season", models.CharField(blank=True, max_length=50, null=True)),
				(
					"region",
					models.CharField(
						blank=True,
						choices=[
							("wd", "World-wide"),
							("eu", "Europe"),
							("as", "Asia"),
							("af", "Africa"),
							("na", "North America"),
							("sa", "South America"),
							("oc", "Oceania"),
						],
						max_length=2,
						null=True,
					),
				),
				(
					"governing_body",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="leagues",
						to="sportsbetting.governingbody",
					),
				),
			],
			options={
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="Division",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("icon", models.ImageField(blank=True, null=True, upload_to="")),
				("name", models.CharField(max_length=100)),
				("hierarchy_level", models.PositiveIntegerField(default=1)),
				(
					"league",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="divisions",
						to="sportsbetting.league",
					),
				),
			],
			options={
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="Play",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				(
					"amount_currency",
					djmoney.models.fields.CurrencyField(
						choices=[
							("XUA", "ADB Unit of Account"),
							("AFN", "Afghan Afghani"),
							("AFA", "Afghan Afghani (1927–2002)"),
							("ALL", "Albanian Lek"),
							("ALK", "Albanian Lek (1946–1965)"),
							("DZD", "Algerian Dinar"),
							("ADP", "Andorran Peseta"),
							("AOA", "Angolan Kwanza"),
							("AOK", "Angolan Kwanza (1977–1991)"),
							("AON", "Angolan New Kwanza (1990–2000)"),
							("AOR", "Angolan Readjusted Kwanza (1995–1999)"),
							("ARA", "Argentine Austral"),
							("ARS", "Argentine Peso"),
							("ARM", "Argentine Peso (1881–1970)"),
							("ARP", "Argentine Peso (1983–1985)"),
							("ARL", "Argentine Peso Ley (1970–1983)"),
							("AMD", "Armenian Dram"),
							("AWG", "Aruban Florin"),
							("AUD", "Australian Dollar"),
							("ATS", "Austrian Schilling"),
							("AZN", "Azerbaijani Manat"),
							("AZM", "Azerbaijani Manat (1993–2006)"),
							("BSD", "Bahamian Dollar"),
							("BHD", "Bahraini Dinar"),
							("BDT", "Bangladeshi Taka"),
							("BBD", "Barbadian Dollar"),
							("BYN", "Belarusian Ruble"),
							("BYB", "Belarusian Ruble (1994–1999)"),
							("BYR", "Belarusian Ruble (2000–2016)"),
							("BEF", "Belgian Franc"),
							("BEC", "Belgian Franc (convertible)"),
							("BEL", "Belgian Franc (financial)"),
							("BZD", "Belize Dollar"),
							("BMD", "Bermudan Dollar"),
							("BTN", "Bhutanese Ngultrum"),
							("BOB", "Bolivian Boliviano"),
							("BOL", "Bolivian Boliviano (1863–1963)"),
							("BOV", "Bolivian Mvdol"),
							("BOP", "Bolivian Peso"),
							("VED", "Bolívar Soberano"),
							("BAM", "Bosnia-Herzegovina Convertible Mark"),
							("BAD", "Bosnia-Herzegovina Dinar (1992–1994)"),
							("BAN", "Bosnia-Herzegovina New Dinar (1994–1997)"),
							("BWP", "Botswanan Pula"),
							("BRC", "Brazilian Cruzado (1986–1989)"),
							("BRZ", "Brazilian Cruzeiro (1942–1967)"),
							("BRE", "Brazilian Cruzeiro (1990–1993)"),
							("BRR", "Brazilian Cruzeiro (1993–1994)"),
							("BRN", "Brazilian New Cruzado (1989–1990)"),
							("BRB", "Brazilian New Cruzeiro (1967–1986)"),
							("BRL", "Brazilian Real"),
							("GBP", "British Pound"),
							("BND", "Brunei Dollar"),
							("BGL", "Bulgarian Hard Lev"),
							("BGN", "Bulgarian Lev"),
							("BGO", "Bulgarian Lev (1879–1952)"),
							("BGM", "Bulgarian Socialist Lev"),
							("BUK", "Burmese Kyat"),
							("BIF", "Burundian Franc"),
							("XPF", "CFP Franc"),
							("KHR", "Cambodian Riel"),
							("CAD", "Canadian Dollar"),
							("CVE", "Cape Verdean Escudo"),
							("KYD", "Cayman Islands Dollar"),
							("XAF", "Central African CFA Franc"),
							("CLE", "Chilean Escudo"),
							("CLP", "Chilean Peso"),
							("CLF", "Chilean Unit of Account (UF)"),
							("CNX", "Chinese People’s Bank Dollar"),
							("CNY", "Chinese Yuan"),
							("CNH", "Chinese Yuan (offshore)"),
							("COP", "Colombian Peso"),
							("COU", "Colombian Real Value Unit"),
							("KMF", "Comorian Franc"),
							("CDF", "Congolese Franc"),
							("CRC", "Costa Rican Colón"),
							("HRD", "Croatian Dinar"),
							("HRK", "Croatian Kuna"),
							("CUC", "Cuban Convertible Peso"),
							("CUP", "Cuban Peso"),
							("CYP", "Cypriot Pound"),
							("CZK", "Czech Koruna"),
							("CSK", "Czechoslovak Hard Koruna"),
							("DKK", "Danish Krone"),
							("DJF", "Djiboutian Franc"),
							("DOP", "Dominican Peso"),
							("NLG", "Dutch Guilder"),
							("XCD", "East Caribbean Dollar"),
							("DDM", "East German Mark"),
							("ECS", "Ecuadorian Sucre"),
							("ECV", "Ecuadorian Unit of Constant Value"),
							("EGP", "Egyptian Pound"),
							("GQE", "Equatorial Guinean Ekwele"),
							("ERN", "Eritrean Nakfa"),
							("EEK", "Estonian Kroon"),
							("ETB", "Ethiopian Birr"),
							("EUR", "Euro"),
							("XBA", "European Composite Unit"),
							("XEU", "European Currency Unit"),
							("XBB", "European Monetary Unit"),
							("XBC", "European Unit of Account (XBC)"),
							("XBD", "European Unit of Account (XBD)"),
							("FKP", "Falkland Islands Pound"),
							("FJD", "Fijian Dollar"),
							("FIM", "Finnish Markka"),
							("FRF", "French Franc"),
							("XFO", "French Gold Franc"),
							("XFU", "French UIC-Franc"),
							("GMD", "Gambian Dalasi"),
							("GEK", "Georgian Kupon Larit"),
							("GEL", "Georgian Lari"),
							("DEM", "German Mark"),
							("GHS", "Ghanaian Cedi"),
							("GHC", "Ghanaian Cedi (1979–2007)"),
							("GIP", "Gibraltar Pound"),
							("XAU", "Gold"),
							("GRD", "Greek Drachma"),
							("GTQ", "Guatemalan Quetzal"),
							("GWP", "Guinea-Bissau Peso"),
							("GNF", "Guinean Franc"),
							("GNS", "Guinean Syli"),
							("GYD", "Guyanaese Dollar"),
							("HTG", "Haitian Gourde"),
							("HNL", "Honduran Lempira"),
							("HKD", "Hong Kong Dollar"),
							("HUF", "Hungarian Forint"),
							("IMP", "IMP"),
							("ISK", "Icelandic Króna"),
							("ISJ", "Icelandic Króna (1918–1981)"),
							("INR", "Indian Rupee"),
							("IDR", "Indonesian Rupiah"),
							("IRR", "Iranian Rial"),
							("IQD", "Iraqi Dinar"),
							("IEP", "Irish Pound"),
							("ILS", "Israeli New Shekel"),
							("ILP", "Israeli Pound"),
							("ILR", "Israeli Shekel (1980–1985)"),
							("ITL", "Italian Lira"),
							("JMD", "Jamaican Dollar"),
							("JPY", "Japanese Yen"),
							("JOD", "Jordanian Dinar"),
							("KZT", "Kazakhstani Tenge"),
							("KES", "Kenyan Shilling"),
							("KWD", "Kuwaiti Dinar"),
							("KGS", "Kyrgystani Som"),
							("LAK", "Laotian Kip"),
							("LVL", "Latvian Lats"),
							("LVR", "Latvian Ruble"),
							("LBP", "Lebanese Pound"),
							("LSL", "Lesotho Loti"),
							("LRD", "Liberian Dollar"),
							("LYD", "Libyan Dinar"),
							("LTL", "Lithuanian Litas"),
							("LTT", "Lithuanian Talonas"),
							("LUL", "Luxembourg Financial Franc"),
							("LUC", "Luxembourgian Convertible Franc"),
							("LUF", "Luxembourgian Franc"),
							("MOP", "Macanese Pataca"),
							("MKD", "Macedonian Denar"),
							("MKN", "Macedonian Denar (1992–1993)"),
							("MGA", "Malagasy Ariary"),
							("MGF", "Malagasy Franc"),
							("MWK", "Malawian Kwacha"),
							("MYR", "Malaysian Ringgit"),
							("MVR", "Maldivian Rufiyaa"),
							("MVP", "Maldivian Rupee (1947–1981)"),
							("MLF", "Malian Franc"),
							("MTL", "Maltese Lira"),
							("MTP", "Maltese Pound"),
							("MRU", "Mauritanian Ouguiya"),
							("MRO", "Mauritanian Ouguiya (1973–2017)"),
							("MUR", "Mauritian Rupee"),
							("MXV", "Mexican Investment Unit"),
							("MXN", "Mexican Peso"),
							("MXP", "Mexican Silver Peso (1861–1992)"),
							("MDC", "Moldovan Cupon"),
							("MDL", "Moldovan Leu"),
							("MCF", "Monegasque Franc"),
							("MNT", "Mongolian Tugrik"),
							("MAD", "Moroccan Dirham"),
							("MAF", "Moroccan Franc"),
							("MZE", "Mozambican Escudo"),
							("MZN", "Mozambican Metical"),
							("MZM", "Mozambican Metical (1980–2006)"),
							("MMK", "Myanmar Kyat"),
							("NAD", "Namibian Dollar"),
							("NPR", "Nepalese Rupee"),
							("ANG", "Netherlands Antillean Guilder"),
							("TWD", "New Taiwan Dollar"),
							("NZD", "New Zealand Dollar"),
							("NIO", "Nicaraguan Córdoba"),
							("NIC", "Nicaraguan Córdoba (1988–1991)"),
							("NGN", "Nigerian Naira"),
							("KPW", "North Korean Won"),
							("NOK", "Norwegian Krone"),
							("OMR", "Omani Rial"),
							("PKR", "Pakistani Rupee"),
							("XPD", "Palladium"),
							("PAB", "Panamanian Balboa"),
							("PGK", "Papua New Guinean Kina"),
							("PYG", "Paraguayan Guarani"),
							("PEI", "Peruvian Inti"),
							("PEN", "Peruvian Sol"),
							("PES", "Peruvian Sol (1863–1965)"),
							("PHP", "Philippine Peso"),
							("XPT", "Platinum"),
							("PLN", "Polish Zloty"),
							("PLZ", "Polish Zloty (1950–1995)"),
							("PTE", "Portuguese Escudo"),
							("GWE", "Portuguese Guinea Escudo"),
							("QAR", "Qatari Riyal"),
							("XRE", "RINET Funds"),
							("RHD", "Rhodesian Dollar"),
							("RON", "Romanian Leu"),
							("ROL", "Romanian Leu (1952–2006)"),
							("RUB", "Russian Ruble"),
							("RUR", "Russian Ruble (1991–1998)"),
							("RWF", "Rwandan Franc"),
							("SVC", "Salvadoran Colón"),
							("WST", "Samoan Tala"),
							("SAR", "Saudi Riyal"),
							("RSD", "Serbian Dinar"),
							("CSD", "Serbian Dinar (2002–2006)"),
							("SCR", "Seychellois Rupee"),
							("SLE", "Sierra Leonean Leone"),
							("SLL", "Sierra Leonean Leone (1964—2022)"),
							("XAG", "Silver"),
							("SGD", "Singapore Dollar"),
							("SKK", "Slovak Koruna"),
							("SIT", "Slovenian Tolar"),
							("SBD", "Solomon Islands Dollar"),
							("SOS", "Somali Shilling"),
							("ZAR", "South African Rand"),
							("ZAL", "South African Rand (financial)"),
							("KRH", "South Korean Hwan (1953–1962)"),
							("KRW", "South Korean Won"),
							("KRO", "South Korean Won (1945–1953)"),
							("SSP", "South Sudanese Pound"),
							("SUR", "Soviet Rouble"),
							("ESP", "Spanish Peseta"),
							("ESA", "Spanish Peseta (A account)"),
							("ESB", "Spanish Peseta (convertible account)"),
							("XDR", "Special Drawing Rights"),
							("LKR", "Sri Lankan Rupee"),
							("SHP", "St. Helena Pound"),
							("XSU", "Sucre"),
							("SDD", "Sudanese Dinar (1992–2007)"),
							("SDG", "Sudanese Pound"),
							("SDP", "Sudanese Pound (1957–1998)"),
							("SRD", "Surinamese Dollar"),
							("SRG", "Surinamese Guilder"),
							("SZL", "Swazi Lilangeni"),
							("SEK", "Swedish Krona"),
							("CHF", "Swiss Franc"),
							("SYP", "Syrian Pound"),
							("STN", "São Tomé & Príncipe Dobra"),
							("STD", "São Tomé & Príncipe Dobra (1977–2017)"),
							("TVD", "TVD"),
							("TJR", "Tajikistani Ruble"),
							("TJS", "Tajikistani Somoni"),
							("TZS", "Tanzanian Shilling"),
							("XTS", "Testing Currency Code"),
							("THB", "Thai Baht"),
							("TPE", "Timorese Escudo"),
							("TOP", "Tongan Paʻanga"),
							("TTD", "Trinidad & Tobago Dollar"),
							("TND", "Tunisian Dinar"),
							("TRY", "Turkish Lira"),
							("TRL", "Turkish Lira (1922–2005)"),
							("TMT", "Turkmenistani Manat"),
							("TMM", "Turkmenistani Manat (1993–2009)"),
							("USD", "US Dollar"),
							("USN", "US Dollar (Next day)"),
							("USS", "US Dollar (Same day)"),
							("UGX", "Ugandan Shilling"),
							("UGS", "Ugandan Shilling (1966–1987)"),
							("UAH", "Ukrainian Hryvnia"),
							("UAK", "Ukrainian Karbovanets"),
							("AED", "United Arab Emirates Dirham"),
							("UYW", "Uruguayan Nominal Wage Index Unit"),
							("UYU", "Uruguayan Peso"),
							("UYP", "Uruguayan Peso (1975–1993)"),
							("UYI", "Uruguayan Peso (Indexed Units)"),
							("UZS", "Uzbekistani Som"),
							("VUV", "Vanuatu Vatu"),
							("VES", "Venezuelan Bolívar"),
							("VEB", "Venezuelan Bolívar (1871–2008)"),
							("VEF", "Venezuelan Bolívar (2008–2018)"),
							("VND", "Vietnamese Dong"),
							("VNN", "Vietnamese Dong (1978–1985)"),
							("CHE", "WIR Euro"),
							("CHW", "WIR Franc"),
							("XOF", "West African CFA Franc"),
							("YDD", "Yemeni Dinar"),
							("YER", "Yemeni Rial"),
							("YUN", "Yugoslavian Convertible Dinar (1990–1992)"),
							("YUD", "Yugoslavian Hard Dinar (1966–1990)"),
							("YUM", "Yugoslavian New Dinar (1994–2002)"),
							("YUR", "Yugoslavian Reformed Dinar (1992–1993)"),
							("ZWN", "ZWN"),
							("ZRN", "Zairean New Zaire (1993–1998)"),
							("ZRZ", "Zairean Zaire (1971–1993)"),
							("ZMW", "Zambian Kwacha"),
							("ZMK", "Zambian Kwacha (1968–2012)"),
							("ZWD", "Zimbabwean Dollar (1980–2008)"),
							("ZWR", "Zimbabwean Dollar (2008)"),
							("ZWL", "Zimbabwean Dollar (2009)"),
						],
						default="USD",
						editable=False,
						max_length=3,
					),
				),
				(
					"amount",
					djmoney.models.fields.MoneyField(
						decimal_places=2,
						default_currency="USD",
						max_digits=10,
						validators=[
							djmoney.models.validators.MinMoneyValidator(
								djmoney.money.Money(5, "USD")
							)
						],
					),
				),
				("placed_datetime", models.DateTimeField(auto_now=True)),
				("paid", models.BooleanField(default=False)),
				("won", models.BooleanField(default=False)),
				(
					"user",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="plays",
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				"verbose_name": "play",
				"verbose_name_plural": "plays",
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="ScheduledGame",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("home_team_final_score", models.IntegerField(blank=True, null=True)),
				("away_team_final_score", models.IntegerField(blank=True, null=True)),
				("location", models.CharField(max_length=100)),
				("start_datetime", models.DateTimeField()),
				(
					"league",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="schedule_games",
						to="sportsbetting.league",
					),
				),
				(
					"sport",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="schedule_games",
						to="sportsbetting.sport",
					),
				),
			],
			options={
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.CreateModel(
			name="BettingLine",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("spread", models.DecimalField(decimal_places=2, max_digits=5)),
				("is_pick", models.BooleanField(blank=True, default=False)),
				("over", models.IntegerField(blank=True, null=True)),
				("under", models.IntegerField(blank=True, null=True)),
				("start_datetime", models.DateTimeField()),
				(
					"game",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="betting_lines",
						to="sportsbetting.scheduledgame",
					),
				),
			],
			options={
				"verbose_name": "betting line",
				"verbose_name_plural": "betting lines",
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.AddField(
			model_name="governingbody",
			name="sport",
			field=auto_prefetch.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name="governing_bodies",
				to="sportsbetting.sport",
			),
		),
		migrations.CreateModel(
			name="Team",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				(
					"logo",
					models.ImageField(blank=True, null=True, upload_to="teams/logos/"),
				),
				(
					"brand",
					models.ImageField(blank=True, null=True, upload_to="teams/brands/"),
				),
				("website", models.URLField(blank=True, null=True)),
				("name", models.CharField(max_length=100)),
				("location", models.CharField(blank=True, max_length=100, null=True)),
				("founding_year", models.PositiveIntegerField(blank=True, null=True)),
				("downloaded", models.BooleanField(default=False, editable=False)),
				(
					"division",
					auto_prefetch.ForeignKey(
						blank=True,
						null=True,
						on_delete=django.db.models.deletion.CASCADE,
						related_name="teams",
						to="sportsbetting.division",
					),
				),
				(
					"league",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="teams",
						to="sportsbetting.league",
					),
				),
			],
			options={
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.AddField(
			model_name="scheduledgame",
			name="away_team",
			field=auto_prefetch.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name="schedule_games_away_team",
				to="sportsbetting.team",
			),
		),
		migrations.AddField(
			model_name="scheduledgame",
			name="home_team",
			field=auto_prefetch.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name="schedule_games_home_team",
				to="sportsbetting.team",
			),
		),
		migrations.AddField(
			model_name="scheduledgame",
			name="winner",
			field=auto_prefetch.ForeignKey(
				blank=True,
				null=True,
				on_delete=django.db.models.deletion.SET_NULL,
				related_name="schedule_game_wins",
				to="sportsbetting.team",
			),
		),
		migrations.CreateModel(
			name="PlayPick",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				(
					"type",
					models.CharField(
						choices=[("sp", "Spread"), ("uo", "Under/Over")], max_length=2
					),
				),
				("is_over", models.BooleanField(blank=True, null=True)),
				(
					"betting_line",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="play_picks",
						to="sportsbetting.bettingline",
					),
				),
				(
					"play",
					auto_prefetch.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="picks",
						to="sportsbetting.play",
					),
				),
				(
					"player",
					auto_prefetch.ForeignKey(
						blank=True,
						null=True,
						on_delete=django.db.models.deletion.SET_NULL,
						related_name="play_picks",
						to="sportsbetting.player",
					),
				),
				(
					"team",
					auto_prefetch.ForeignKey(
						blank=True,
						null=True,
						on_delete=django.db.models.deletion.SET_NULL,
						related_name="play_picks",
						to="sportsbetting.team",
					),
				),
			],
			options={
				"verbose_name": "pick",
				"verbose_name_plural": "picks",
				"abstract": False,
				"base_manager_name": "prefetch_manager",
			},
			managers=[
				("objects", django.db.models.manager.Manager()),
				("prefetch_manager", django.db.models.manager.Manager()),
			],
		),
		migrations.AddField(
			model_name="player",
			name="team",
			field=auto_prefetch.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name="players",
				to="sportsbetting.team",
			),
		),
		migrations.AddConstraint(
			model_name="league",
			constraint=models.UniqueConstraint(
				fields=("name", "governing_body"),
				name="unique_league_per_governing_body",
			),
		),
		migrations.AddConstraint(
			model_name="bettingline",
			constraint=models.CheckConstraint(
				condition=models.Q(
					models.Q(("under__isnull", True), ("over__isnull", True)),
					models.Q(("under__isnull", False), ("over__isnull", False)),
					_connector="OR",
				),
				name="betting_line_validate_under_over",
				violation_error_message="Must populate both under and over, or leave both blank.",
			),
		),
		migrations.AddConstraint(
			model_name="team",
			constraint=models.UniqueConstraint(
				fields=("name", "league"), name="unique_team_per_league"
			),
		),
		migrations.AddConstraint(
			model_name="team",
			constraint=models.UniqueConstraint(
				fields=("name", "division"), name="unique_team_per_division"
			),
		),
		migrations.AddConstraint(
			model_name="scheduledgame",
			constraint=models.UniqueConstraint(
				fields=("home_team", "away_team", "start_datetime"),
				name="unique_scheduled_game",
			),
		),
		migrations.AddConstraint(
			model_name="scheduledgame",
			constraint=models.CheckConstraint(
				condition=models.Q(("home_team", models.F("away_team")), _negated=True),
				name="scheduled_game_home_team_not_away_team",
				violation_error_message="Home and away teams cannot be the same.",
			),
		),
		migrations.AddConstraint(
			model_name="playpick",
			constraint=models.UniqueConstraint(
				fields=("play", "betting_line", "type"), name="unique_play_pick"
			),
		),
	]
