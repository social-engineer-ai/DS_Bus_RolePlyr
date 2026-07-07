"""Manual lenient overrides for the BADM 576 final, based on detailed review
of every sub-half-credit response.

Pattern rules applied uniformly:
- Q33 reversed direction WITH cost asymmetry recognized: 0->2 or 1->2.5
- Q33 picked the 0.5-default trap with no asymmetry: stays 0
- Q24 'no bias' conclusion BUT mediation by attendance recognized: bump +0.5 to +1
- Q30 hint of any one of the four conditions: 0->1, 0.5->1.5, 1->1.5; named all four (no justification): bump +1
- Q31 hint of subgroup/aggregate distinction: bump +0.5 to +1
- Q34 'rich get richer' / popularity loop named: bump +0.5 to +1
- Q23/Q25/Q26/Q27/Q28/Q29/Q21 hint of the right idea: small bumps
- Reverses-definitions or completely off-topic: no change
- Blank or near-blank: no change

Each override is upside-only. Reasoning is preserved + appended with manual note.
"""

import json
import subprocess

KEY = "/c/Users/ashishk/Dropbox/My PC (BUS-P10E67720)/Documents/Development/LLM_Role_Player/stakeholdersim-key.pem"
SSH_HOST = "ec2-user@3.90.88.174"
QUIZ_ID = "c400cb0d-9fc9-490e-83ab-6f93d7f0fac4"


# (answer_id, new_score, manual_note_appended_to_reasoning)
OVERRIDES = [
    # === Q33 — reversed direction WITH cost asymmetry (clear understanding, wrong direction) ===
    ("2eadfbdb-15aa-46d8-8865-3ba3469ffb36", 2.5, "Manual override: cost asymmetry FN>FP correctly identified; only the direction is flipped. Per leniency rule (any clear hint of understanding = reward), bump from 1 -> 2.5."),  # jpi5
    ("6c6b0ba3-1404-4ae0-936a-c05b50f93609", 2.0, "Manual override: identifies cost asymmetry correctly; reasoning is internally contradictory but the trade-off insight is present. Bump 0 -> 2."),  # Hind
    ("57e704ac-3f44-4ef4-84f5-a17491f38d43", 2.0, "Manual override: cost asymmetry clearly identified ('losing $20 less worse than $800'). Wrong direction only. Bump 1 -> 2."),  # smagha2
    ("c111192c-95f2-40ff-bbee-1a13664c2bb1", 2.0, "Manual override: cost asymmetry recognized ('FP=20 much lower than FN=800'). Direction flipped. Bump 0 -> 2."),  # yanzhuy2
    ("236c4450-2712-4343-b75e-890cfd1a13e1", 2.0, "Manual override: 'FN costlier than FP' is the correct asymmetry insight. Direction flipped. Bump 0 -> 2."),  # sn48

    # === Q24 — 'no gender bias' wrong conclusion BUT mediation by attendance recognized ===
    ("cbe3a626-209e-4023-9cb5-b9b2b25f2e9a", 2.0, "Manual override: correctly identifies attendance as the mediator and that gap shifts away from gender. Wrong final conclusion ('no gender bias') is one-step removed; the mediation insight is present. Bump 1.5 -> 2."),  # anm20
    ("53d5ddc7-9406-4f57-a21e-ef5ede190ebb", 2.0, "Manual override: correctly identifies training-attendance as confounder absorbing the gender coefficient. Final 'no bias' conclusion is wrong but mediation is clearly understood. Bump 1.5 -> 2."),  # jialinx3
    ("5f8dfaa7-7aae-4867-9754-e3761f56232d", 2.0, "Manual override: notes coefficient vanishes when training added AND identifies attendance gap by gender. The mediation mechanism is clearly grasped. Bump 1 -> 2."),  # Hind
    ("3c999305-536b-40bd-895a-ec6c61be0360", 1.5, "Manual override: mentions training-attendance impacts promotion. Slim but a hint of the mediation. Bump 1 -> 1.5."),  # lingd2
    ("4576f2e8-5496-4627-b011-de6087e5fcf3", 2.0, "Manual override: 'training attendance, not gender itself' is exactly the mediation insight. Bump 1.5 -> 2."),  # zong7
    ("ef1b1623-a4b7-4d60-9a4f-914cde180bff", 1.5, "Manual override: notes men attend training less than women — that's the upstream mechanism. Wrong conclusion but real insight. Bump 0.5 -> 1.5."),  # tipjira2
    ("eb022428-dbeb-459f-8202-0631b36cf927", 1.5, "Manual override: identifies training drives promotions, not gender directly. Confused phrasing but the mechanism is there. Bump 1 -> 1.5."),  # emaads2

    # === Q31 — partial subgroup/aggregate hint ===
    ("eae76670-0ada-498b-95d8-225caaee912d", 2.0, "Manual override: 'who is in the data' + 'why does it not work on engineering jobs' gestures at the subgroup vs aggregate framing. Bump 1.5 -> 2."),  # amajum2
    ("0c98cf43-9da1-4d70-8f44-3c9b3bd8c469", 2.5, "Manual override: 'overall accuracy not specific for one exact person' is the right aggregate-vs-subgroup intuition. Bump 2 -> 2.5."),  # lingd2
    ("173004ff-1f01-417a-b553-6f83eb43efd5", 2.5, "Manual override: 'product manager and recruiter seeing different type of data so they have different result' is roughly the unit-of-analysis idea. Bump 2 -> 2.5."),  # shunluo2
    ("cb14bb0b-5525-49b1-8801-b588e043089b", 1.5, "Manual override: gestures at metrics differing for stakeholders + asks for additional info. Bump 1 -> 1.5."),  # jialinx3
    ("2390e5b9-7544-4d4b-bb18-7f499c5a60f7", 2.5, "Manual override: identifies overall vs specific case difference. Misframes subgroup as single candidate but the aggregate/subgroup intuition is there. Bump 2 -> 2.5."),  # qiaoqil2
    ("dfc4cfff-851e-4e80-a6f8-bba5243cf5f5", 2.5, "Manual override: 'accuracy hide poor performance in the focused group such as engineering jobs' is exactly the subgroup hidden by aggregate insight. Bump 2 -> 2.5."),  # tipjira2
    ("01eef78e-4720-4c73-9ed6-458472b22012", 2.5, "Manual override: 'platform average may hide poor performance in subgroups' is exactly right. Bump 2 -> 2.5."),  # zong7

    # === Q34 — popularity loop / rich-get-richer hint ===
    ("63a575d9-0533-47f1-b64f-8b38003d1690", 2.0, "Manual override: 'richer get more richer, popular songs more likely to be recommended' is exactly the popularity-loop mechanism. Bump 1 -> 2."),  # shunluo2
    ("520f02a5-456e-4fa0-b668-f44c7af2d080", 2.5, "Manual override: explicitly names 'popularity loop' AND describes feedback ('receive more interaction, keep recommend'). Just lacks the metric/mitigation pieces. Bump 2 -> 2.5."),  # zong7
    ("6abde442-f98b-4cb7-abdc-a781c599c620", 1.5, "Manual override: notes recommendations only based on listening history and unusual songs disregarded. Bump 1 -> 1.5."),  # sn48
    ("f998be66-cf54-4fa7-8962-980c9fd808db", 2.5, "Manual override: 'narrowing the samples' + 'always uses past data' captures the loop intuition + proposes diversity injection. Bump 2 -> 2.5."),  # lingd2

    # === Q30 — Spotify vs loans, condition hints ===
    ("247160c2-6196-433e-bcc5-e2577b8dccf4", 2.0, "Manual override: 'forms preference (Spotify) vs exists preference (loan)' is exactly the latent-taste contrast. Bump 0.5 -> 2."),  # jpi5
    ("4c3a84dc-9a4e-4f4a-a1b0-7ee95865a692", 1.5, "Manual override: names 'latent factors' which is the latent-taste condition. Bump 0.5 -> 1.5."),  # Hind
    ("1ea5f639-f836-4a31-b159-0f62e7a68bcf", 2.0, "Manual override: names dense interactions and vast catalog (two conditions). No justification but two correct names. Bump 1 -> 2."),  # jialinx3
    ("4c46d893-0185-41c8-a31e-d71cb6b0d46f", 2.0, "Manual override: lists ALL FOUR conditions by name (latent taste, dense interaction, large catalog, low-cost mistakes). No justification but full vocabulary recognition. Bump 1 -> 2."),  # yangf5
    ("a5de6f5e-fb5f-4692-a7e8-e49f0245fdb0", 1.5, "Manual override: contrasts Spotify (stable preferences) vs loans (risky / macroeconomic) — gestures at cheap-mistakes asymmetry. Bump 0.5 -> 1.5."),  # qiaoqil2
    ("a72b4643-8cd3-4797-b3fd-d75d5b4bdbad", 1.0, "Manual override: 'embeddings' for Spotify gestures at latent-taste though framing is muddled. Bump 0 -> 1."),  # smagha2
    ("0397b16e-55c0-4ae7-bddb-17d8f078bd24", 0.5, "Manual override: vague gesture at past-data feedback for Spotify but inverts the loan reasoning. Bump 0 -> 0.5."),  # xliu177

    # === Q25 — bias vs variance ===
    ("a0f2452d-9942-40a5-a3b9-6b19ca11b95f", 2.0, "Manual override: explicitly states 'bias is a specification problem; variance is sample sensitivity' — that's the textbook framing in plain words. Just missing fixes. Bump 1.5 -> 2."),  # dxu28
    ("c1e79552-1385-47bc-8445-1ab783c69574", 2.0, "Manual override: one-size-fits-all (bias/underfit) vs tailored (variance/overfit) is a recognizable plain-English mapping. Bump 1 -> 2."),  # emaads2
    ("3e6dff3c-cd6c-4b12-ab0f-a033f42ce306", 1.0, "Manual override: gestures at 'more data doesn't fix bias' via the luxury-cars example. Bump 0.5 -> 1."),  # qm9
    ("7afedffa-07fd-4c60-9553-27f04f433cb8", 1.5, "Manual override: 'systematically wrong in one direction' for bias and 'too unstable' for variance are clean plain-language definitions. Regularization for variance is correct. Only the 'more data fixes bias' tripped the rubric. Bump 1 -> 1.5."),  # siyic5
    ("1d5a615a-482d-43a4-b0d4-879ed5c37e74", 1.5, "Manual override: variance defined as data-driven, bias defined as coefficient/prediction sensitivity. Confused but engages with both. Bump 1 -> 1.5."),  # smagha2
    ("f59bddd1-94f2-47da-8216-a649ed5e5983", 1.5, "Manual override: bias correctly framed as 'specification, including incorrect variables'. Variance/underfitting confusion drops it but the bias half is right. Bump 1 -> 1.5."),  # sn48
    ("2866584f-8e07-4d74-8afe-a030f4b49a34", 1.5, "Manual override: 'wrong in one direction' for bias and 'too unstable' for variance are clean plain-language. Bump 1 -> 1.5."),  # tipjira2

    # === Q23 — underlying lesson ===
    ("08cc7961-e3c0-4b3f-b55e-d50fe01e8256", 1.5, "Manual override: 'care more about what is not included in the model' is roughly the conditional-on-spec insight. Bump 1 -> 1.5."),  # jialinx3
    ("8ec87992-222c-45d4-91b1-b82f80f3ffd6", 1.5, "Manual override: 'control other things constant to see which element affect the model most' is adjacent to the lesson. Bump 1 -> 1.5."),  # qiaoqil2
    ("e3f4c21f-a57e-4a5f-a6e3-a690e11c4b31", 1.5, "Manual override: provides a Berkeley-style example with subgroup reversal — that's Simpson's understanding even if it answers a slightly different question. Bump 1 -> 1.5."),  # qm9
    ("d199459c-8f1d-4362-99e9-002f8024ab37", 2.0, "Manual override: defines confounder + mentions aggregation/subgroups + 'consider in different business cases' — covers the unifying idea. Bump 1.5 -> 2."),  # yanzhuy2
    ("834bc95d-2f1e-4ee0-b9cb-20cda43d35dd", 2.0, "Manual override: 'subgroup that can be flipped whole story' is exactly the Simpson's-style insight in plain words. Bump 1.5 -> 2."),  # tipjira2

    # === Q26 — train/test ===
    ("946fdd5a-fbab-4065-9a5c-6f96e886613c", 1.5, "Manual override: notes train/test split changes insights — adjacent to the rule-generalization point. Bump 1 -> 1.5."),  # Hind
    ("c0a0a09e-5a21-4cbb-ad76-b93f71ef5ce6", 2.0, "Manual override: 'special case not common one' captures the memorization-vs-generalization concern in plain words. Bump 1.5 -> 2."),  # lingd2
    ("331a95f9-653c-47bb-9366-5def95167951", 1.5, "Manual override: 'training perfectly might ignore another group of data' is the right transfer concern. Bump 1 -> 1.5."),  # dxu28

    # === Q27 — residuals ===
    ("c8e3e81e-0995-4eac-a9b9-478149938006", 1.5, "Manual override: 'residual reflects gap between predictions and real data' + concrete real-estate example. Doesn't reach the constructed-variable insight but isn't wrong. Bump 1 -> 1.5."),  # lingd2
    ("47aeb978-a5bb-494c-af7a-c0786470fccd", 1.5, "Manual override: 'residual left in the regression that was still unexplained' acknowledges residuals carry unexplained signal. Bump 1 -> 1.5."),  # smagha2
    ("d66e8ffa-bb1c-4ef8-8165-f1a01da20130", 2.0, "Manual override: 'residual is what further conclusions can be drawn from same data' — that's exactly the construct-an-unmeasurable framing in plain words. Bump 1.5 -> 2."),  # sn48

    # === Q28 — recall vs precision ===
    ("2dc289e2-c338-4c46-bc95-bcf7b9a6a037", 2.0, "Manual override: 'recall is missed opportunity, precision is what happened was good' is a clean plain-English framing of both. Examples are confused but definitions are good. Bump 1.5 -> 2."),  # dpurwar2
    ("6ec1a054-ed7f-4daa-a8f4-80e4745d7c84", 1.5, "Manual override: provides correct formulas for both metrics + a delay-classification example. Doesn't pick which matters but understanding shown. Bump 1 -> 1.5."),  # emaads2
    ("250e8102-2489-4f90-b110-62f3f4b2569c", 2.0, "Manual override: COVID-19 example for recall is correct cost-of-miss reasoning. Bump 1.5 -> 2."),  # jpi5
    ("8dea0f23-900c-4010-bf2b-b07078005a01", 1.5, "Manual override: 'recall = catching misses, precision = correctness' is the right plain-English framing. Bump 1 -> 1.5."),  # qiaoqil2
    ("4cb487c5-6abb-43b1-baf0-bf693afa090a", 1.0, "Manual override: framing is reversed but the student does name both metrics and provide examples. Some understanding is there. Bump 0 -> 1."),  # rreye3
    ("501a47a3-91af-4ecd-9de9-57f7ed207044", 2.0, "Manual override: hospital + false-negative example correctly identifies cost-of-miss. Bump 1.5 -> 2."),  # shunluo2
    ("95d7e60a-6db7-45e1-b813-f89cdae26b93", 1.0, "Manual override: identifies that COVID FN is costly and customer LTV-vs-retention cost — the underlying cost-asymmetry idea is present, framing is reversed. Bump 0 -> 1."),  # smagha2
    ("9baedcb2-53bc-4b8e-a88f-a6491773dfa5", 1.0, "Manual override: COVID example with 'lower threshold to decrease cost of FP' shows confused mechanics but real engagement with cost trade-offs. Bump 0.5 -> 1."),  # yanzhuy2

    # === Q29 — curse of dimensionality ===
    ("aaa27ed4-e28e-4bfa-851b-b2f815b15fd2", 2.0, "Manual override: states 'similarity weakens as dimensions grow' — that IS the mechanism named. Bump 1.5 -> 2."),  # dxu28
    ("71063946-8863-4a7f-b1de-6eca9da70142", 1.5, "Manual override: mentions overfitting + suggests PCA — adjacent to dimensionality reduction. Bump 1 -> 1.5."),  # emaads2
    ("47d6df0d-c250-4b4b-825c-40176cafa435", 2.0, "Manual override: names 'multidimensionality' (close to curse of dimensionality) + describes points in multidimensional space + decreased similarity. The mechanism + adjacent name. Bump 1.5 -> 2."),  # Hind
    ("b34b0d94-43c7-4867-bf4f-45d959f0b33c", 2.0, "Manual override: 'too similar customers may not exist' is exactly the right intuition (every point becomes unique). Bump 1.5 -> 2."),  # qm9
    ("4a2c9f46-269c-4d4d-a1fa-72b0e594db29", 0.5, "Manual override: 'fewer dimensions, compare more easily' gestures at PCA/dim reduction. Off-topic for the question but engages. Bump 0 -> 0.5."),  # shunluo2
    ("129a4530-8571-4823-b747-eea77781a2f9", 2.0, "Manual override: 'features added customer became less and less different' + 'unique eventually they cant focus all' captures the uniqueness/distance-flattening. Bump 1.5 -> 2."),  # tipjira2

    # === Q21 — unit of observation ===
    ("a478042c-6bb1-4570-a6f8-9888d727c026", 2.0, "Manual override: 'one row in a dataset gives the unit of observation' is the correct definition. Example is weak but definition is right. Bump 1.5 -> 2."),  # emaads2
    ("82ee2f80-ab77-49b8-9c6a-fb9e8b9e0bb2", 1.5, "Manual override: definition adequate, only one unit named. Bump 1 -> 1.5."),  # yangf5
    ("1b340af0-d935-445a-80d7-fe8cd2618218", 2.0, "Manual override: 'unit of observation is what one row in the dataset' is the textbook definition. No example but core concept right. Bump 1.5 -> 2."),  # zong7
    ("ba269a5e-ccc8-46b7-82d6-c6a97fa1677f", 1.5, "Manual override: 'thing we focus on' + bank-loan applicant example is a partial concept. Bump 1 -> 1.5."),  # lingd2
]


def run_psql(sql: str) -> str:
    cmd = [
        "ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
        f"sudo docker exec stakeholder_sim_db psql -U stakeholder_sim -d stakeholder_sim -c \"{sql}\"",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")
    return result.stdout


def main():
    print(f"Applying {len(OVERRIDES)} manual overrides...")
    for ans_id, new_score, note in OVERRIDES:
        # Append the note to the existing reasoning so we keep both LLM and manual rationales.
        # SQL: append " | MANUAL: <note>" to the existing reasoning.
        esc_note = note.replace("'", "''")
        sql = (
            f"UPDATE quiz_answers SET points_awarded = {new_score}, "
            f"grader_reasoning = grader_reasoning || ' | MANUAL: {esc_note}', "
            f"graded_by = 'instructor', needs_review = false "
            f"WHERE id = '{ans_id}'"
        )
        run_psql(sql)
    print("All overrides applied.")

    # Recompute attempt totals
    print("\nRecomputing attempt totals...")
    recompute_sql = (
        f"UPDATE quiz_attempts qa SET score = sub.s FROM "
        f"(SELECT attempt_id, SUM(points_awarded) AS s FROM quiz_answers GROUP BY attempt_id) sub "
        f"WHERE qa.id = sub.attempt_id AND qa.quiz_id='{QUIZ_ID}'"
    )
    run_psql(recompute_sql)

    # Print final scores
    final_sql = (
        "SELECT u.email AS netid, u.name, "
        "SUM(CASE WHEN q.question_type='mcq' THEN ans.points_awarded ELSE 0 END) AS section_a, "
        "SUM(CASE WHEN q.question_type='short_answer' AND q.points=4 THEN ans.points_awarded ELSE 0 END) AS section_b, "
        "SUM(CASE WHEN q.question_type='short_answer' AND q.points=5 THEN ans.points_awarded ELSE 0 END) AS section_c, "
        "qa.score AS total "
        "FROM quiz_attempts qa JOIN users u ON u.id=qa.student_id "
        "JOIN quiz_answers ans ON ans.attempt_id=qa.id "
        "JOIN quiz_questions q ON q.id=ans.question_id "
        f"WHERE qa.quiz_id='{QUIZ_ID}' AND qa.is_submitted=true "
        "GROUP BY u.email, u.name, qa.id, qa.score "
        "ORDER BY qa.score DESC"
    )
    print("\n" + "=" * 72)
    print("FINAL SCORES (after manual lenient overrides)")
    print("=" * 72)
    print(run_psql(final_sql))


if __name__ == "__main__":
    main()
