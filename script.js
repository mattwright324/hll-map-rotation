(function () {
    $(window).init(function () {
        console.log("window init")

        const weightsTable = $("#map-weights").DataTable({
            dom: "",
            columns: [{title: "Map"},{title: "Seeding"},{title: "Stress"},{title: "Weight"}],
            columnDefs: [{
                "defaultContent": "",
                "targets": "_all"
            }],
            order: [],
            lengthMenu: [[10, 25, 50, 100, 250, -1], [10, 25, 50, 100, 250, "All"]],
            deferRender: true,
            bDeferRender: true,
            paging: false,
            searching: false,
            header: false,
            pageLength: -1
        });
        const btnGenerate = $("#generate");
        const configInput = $("#configInput");
        const checkUseWeight = $("#checkUseWeight");
        const checkSeeding = $("#checkSeed");
        const inputStressDist = $("#min-stress");
        const inputGenDupeDist = $("#min-gen-dupe");
        const inputExactDupeDist = $("#min-exact-dupe");

        const radioPretty = $("#radioPretty");
        const radioAuto = $("#radioAuto");
        const radioIni = $("#radioIni");
        const radioIniPath = $("#radioIniPath");
        const resultsPrettyDiv = $("#results-pretty");
        const resultsAutoDiv = $("#results-autosettings");
        const resultsIniDiv = $("#results-ini");
        const resultsIniPathDiv = $("#results-ini-path");

        function hideAll() {
            resultsPrettyDiv.hide()
            resultsAutoDiv.hide()
            resultsIniDiv.hide()
            resultsIniPathDiv.hide()
        }

        radioPretty.click(function () {hideAll(); resultsPrettyDiv.show()})
        radioAuto.click(function () {hideAll(); resultsAutoDiv.show()})
        radioIni.click(function () {hideAll(); resultsIniDiv.show()})
        radioIniPath.click(function () {hideAll(); resultsIniPathDiv.show()})

        $("input[type='number']").inputSpinner();
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        // https://stackoverflow.com/a/55671924
        function weighted_random(options) {
            let i;
            let weights = [options[0].weight];
            for (i = 1; i < options.length; i++)
                weights[i] = options[i].weight + weights[i - 1];

            const random = Math.random() * weights[weights.length - 1];
            for (i = 0; i < weights.length; i++)
                if (weights[i] > random) break;

            return options[i];
        }

        function random(options) {
            return options[Math.floor(Math.random()*options.length)]
        }

        function map_options_from_config(config) {
            const options = []

            for (let i = 0; i < csvmaps.length; i++) {
                const map = csvmaps[i];

                let append = false
                if (config.warfare && map.mode === "warfare" && (
                    config.day && map.variant === "day" || config.night && map.variant === "night")) {
                    append = true
                }
                if (config.offensive && map.mode === "offensive" && (
                    config.axis && map.variant === "axis" || config.allies && map.variant === "allies")) {
                    append = true
                }

                let append_stress = false
                if (config.stress && map.stress) append_stress = true
                if (config.nonstress && !map.stress) append_stress = true

                let append_seed = false
                if (config.seeding === null) append_seed = true
                if (config.seeding === true && map.seeding) append_seed = true

                if (append && append_stress && append_seed) {
                    options.push(map)
                }
            }

            return options;
        }

        btnGenerate.click(function () {
            btnGenerate.prop("disabled", true)
            resultsPrettyDiv.html("")
            resultsAutoDiv.html("")
            resultsIniDiv.html("")

            for (let i = 0; i < csvmaps.length; i++) {
                const item = csvmaps[i]

                item.seeding = $("#seeding--" + item.map).is(":checked")
                item.stress = $("#stress--" + item.map).is(":checked")
                item.weight = Number($("#weight--" + item.map).val())
            }

            console.log("Custom map settings", csvmaps)

            const configMatches = [...configInput.val().matchAll(/((\d+)-?(\d+)?)([awdnoguste]+)/gi)]
            const configs = []
            for (let i = 0; i < configMatches.length; i++) {
                const match = configMatches[i];
                const config = {
                    str: match[0].toLowerCase(),
                    range: [Number(match[2]),Number(match[3] || match[2])],
                    warfare: false, day: false, night: false,
                    offensive: false, axis: false, allies: false,
                    stress: false, nonstress: false, seeding: null
                }

                const str = config.str;
                if (str.includes("a")) {
                    config.warfare = true
                    config.day = true
                    config.night = true
                    config.offensive = true
                    config.axis = true
                    config.allies = true
                    config.stress = true
                    config.nonstress = true
                    config.seeding = null
                }
                if (str.includes("w")) {
                    config.warfare = true
                    if (str.includes("d") || str.includes("n")) {
                        config.day = str.includes("d")
                        config.night = str.includes("n")
                    } else {
                        config.day = true
                        config.night = true
                    }
                }
                if (str.includes("o")) {
                    config.offensive = true
                    if (str.includes("g") || str.includes("u")) {
                        config.axis = str.includes("g")
                        config.allies = str.includes("u")
                    } else {
                        config.axis = true
                        config.allies = true
                    }
                }
                if (str.includes("s") || str.includes("t")) {
                    config.stress = str.includes("s")
                    config.nonstress = str.includes("t")
                } else {
                    config.stress = true
                    config.nonstress = true
                }
                if (str.includes("e")) {
                    config.seeding = str.includes("e")
                }

                configs.push(config)
            }
            console.log("Configs", configs)

            const weighted = checkUseWeight.is(":checked");
            const rotation = []
            for (let i = 0; i < configs.length; i++) {
                const config = configs[i];
                const min = Math.min(config.range[0], config.range[1])
                const max = Math.max(config.range[0], config.range[1])
                const options = map_options_from_config(config)
                const amount = Math.min(options.length, Math.floor(min + Math.random()*(max - min + 1)))
                console.log("Config %s options", config.str, options)

                function check_good_result(result) {
                    if (!result) {
                        return false
                    }

                    let len = rotation.length;

                    const exactDist = Number(inputExactDupeDist.val())
                    {
                        let l = len-exactDist
                        if (exactDist === -1 || l < 0) l = 0
                        for (let j = l; j < len; j++) {
                            if (result.map === rotation[j].map) {
                                return false
                            }
                        }
                    }

                    const genDist = Number(inputGenDupeDist.val())
                    {
                        let l = len-genDist
                        if (genDist === -1 || l < 0) l = 0
                        for (let j = l; j < len; j++) {
                            if (result.map.split('_')[0] === rotation[j].map.split("_")[0]) {
                                return false
                            }
                        }
                    }

                    const stressDist = Number(inputStressDist.val())
                    if (result.stress) {
                        let l = len-stressDist
                        if (stressDist === -1 || l < 0) l = 0
                        for (let j = l; j < len; j++) {
                            if (rotation[j].stress) {
                                return false
                            }
                        }
                    }


                    return true
                }

                for (let j = 0; j < amount; j++) {
                    while (options.length > 0) {
                        let good_options = []
                        for (let k = 0; k < options.length; k++) {
                            if (check_good_result(options[k])) {
                                good_options.push(options[k])
                            }
                        }

                        if (good_options.length === 0) {
                            console.log("No more good options to pick from")
                            break
                        }

                        const result = weighted ? weighted_random(good_options) : random(good_options);
                        if (check_good_result(result)) {
                            rotation.push(result)
                            break
                        }
                    }
                }
            }

            const seed_rotation = []
            let seed_temp = []
            for (let i = 0; i < csvmaps.length; i++) {
                if (csvmaps[i].seeding) {
                    seed_temp.push(csvmaps[i])
                    seed_rotation.push("")
                }
            }
            // Match index
            for (let i = 0; i < seed_temp.length; i++) {
                if (i > rotation.length) break
                if (rotation[i].seeding) {
                    seed_rotation[i] = rotation[i]
                }
            }
            console.log(seed_temp)
            seed_temp = seed_temp.filter(e => seed_rotation.indexOf(e) === -1)
            console.log(seed_temp)
            console.log(seed_rotation)
            // Fill in blanks
            for (let i = 0; i < seed_rotation.length; i++) {
                if (!seed_rotation[i]) {
                    seed_rotation[i] = seed_temp.pop()
                }
            }

            const map_names = []
            for (let i = 0; i < rotation.length; i++) {
                const item = rotation[i]
                map_names.push(item.map)

                resultsPrettyDiv.append(
                    `<div class="map-result">
                        <img src="./maps/${item.map.split("_")[0]}.webp">
                        <div style="display:inline-block">
                            ${item.map.split("_")[0]}
                            <br>
                            <small class="text-muted">${item.map}</small>
                        </div>
                        <span class="badge rounded-pill ${item.mode}">${item.mode}</span>
                        <span class="badge rounded-pill bg-secondary ${item.variant}">${item.variant}</span>
                        <span class="badge rounded-pill bg-success seeding-${Boolean(item.seeding)}">seeding</span>
                        <span class="badge rounded-pill bg-danger seeding-${Boolean(item.stress)}">stress</span>
                    </div>`)
            }

            const seed_names = []
            for (let i = 0; i < seed_rotation.length; i++) {
                seed_names.push(seed_rotation[i].map)
            }

            const autoJson = JSON.stringify({"rotation": map_names}, null, 4);
            const autoSeedJson = JSON.stringify({"rotation": seed_names}, null, 4);
            resultsAutoDiv.html(`<pre><code>Live rotation:\n${autoJson}\n\nSeeding rotation:\n${autoSeedJson}</code></pre>`)
            resultsIniDiv.html(`<pre><code>${map_names.join("<br>")}</code></pre>`)
            resultsIniPathDiv.html(`<pre><code>/Game/Maps/${map_names.join("<br>/Game/Maps/")}</code></pre>`)

            btnGenerate.prop("disabled", false)
        })

        Papa.parse("./hll_rcon_maps.csv", {
            download: true,
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: function (results, file) {
                console.log("Parsing complete:", results, file);

                window.csvmaps = results.data;

                const rows = []
                for (let i = 0; i < results.data.length; i++) {
                    const item = results.data[i];
                    rows.push([
                        `<span>
                            ${item.map}
                            <br>
                            <span class="badge rounded-pill ${item.mode}">${item.mode}</span>
                            <span class="badge rounded-pill bg-secondary ${item.variant}">${item.variant}</span>
                        </span>`,
                        `<div class="form-check">
                            <input class="form-check-input" type="checkbox" value="" id="seeding--${item.map}" ${item.seeding ? "checked":""}>
                            <label class="form-check-label" for="seeding--${item.map}">
                                Seeding
                            </label>
                        </div>`,
                        `<div class="form-check">
                            <input class="form-check-input" type="checkbox" value="" id="stress--${item.map}" ${item.stress ? "checked":""}>
                            <label class="form-check-label" for="stress--${item.map}">
                                Stress
                            </label>
                        </div>`,
                        `<input id="weight--${item.map}" class="form-control form-control-sm" type="number" value="${item.weight}" min="0" style="min-width:80px">`
                    ])
                }

                weightsTable.rows.add(rows).draw(false);
                weightsTable.columns.adjust().draw(false);

                btnGenerate.prop("disabled", false)
                btnGenerate.click()
            }
        })

        const autoRemoveMapsRule = {
            "commands": {
                "do_remove_maps_from_rotation": {
                    "maps": [
                        "elalamein_warfare",
                        "foy_warfare",
                        "foy_warfare_night",
                        "hill400_warfare",
                        "hurtgenforest_warfare_V2",
                        "hurtgenforest_warfare_V2_night",
                        "kharkov_warfare",
                        "kursk_warfare",
                        "kursk_warfare_night",
                        "purpleheartlane_warfare",
                        "purpleheartlane_warfare_night",
                        "remagen_warfare",
                        "remagen_warfare_night",
                        "stalingrad_warfare",
                        "carentan_offensive_ger",
                        "carentan_offensive_us",
                        "driel_offensive_ger",
                        "driel_offensive_us",
                        "elalamein_offensive_ger",
                        "elalamein_offensive_CW",
                        "foy_offensive_ger",
                        "foy_offensive_us",
                        "hill400_offensive_ger",
                        "hill400_offensive_US",
                        "hurtgenforest_offensive_ger",
                        "hurtgenforest_offensive_US",
                        "kharkov_offensive_ger",
                        "kharkov_offensive_rus",
                        "kursk_offensive_ger",
                        "kursk_offensive_rus",
                        "omahabeach_offensive_ger",
                        "omahabeach_offensive_us",
                        "purpleheartlane_offensive_ger",
                        "purpleheartlane_offensive_us",
                        "remagen_offensive_ger",
                        "remagen_offensive_us",
                        "stalingrad_offensive_ger",
                        "stalingrad_offensive_rus",
                        "stmariedumont_off_ger",
                        "stmariedumont_off_us",
                        "stmereeglise_offensive_ger",
                        "stmereeglise_offensive_us",
                        "utahbeach_offensive_ger",
                        "utahbeach_offensive_us"
                    ]
                }
            },
            "conditions": {
                "time_of_day": {
                    "max": "23:00",
                    "min": "6:00",
                    "not": true,
                    "timezone": "America/New_York"
                }
            }
        }

        $("#auto-removebadmaps").html(JSON.stringify(autoRemoveMapsRule, null, 4))

    })
}());
