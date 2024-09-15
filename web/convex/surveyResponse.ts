import { getAuthUserId } from "@convex-dev/auth/server";
import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const listSurveyResponses = query({
  args: {},
  handler: async (ctx) => {
    // Fetch the most recent survey responses.
    const surveyResponses = await ctx.db.query("survey_responses").order("desc").take(100);
    // Add the author's name to each response.
    return Promise.all(
      surveyResponses.map(async (response) => {
        const { name, email } = (await ctx.db.get(response.userId))!;
        return { ...response, author: name ?? email! };
      })
    );
  },
});

export const submitSurveyResponses = mutation({
  args: { responses: v.array(v.object({ body: v.string(), author: v.string() })) },
  handler: async (ctx, { responses }) => {
    const userId = await getAuthUserId(ctx);
    if (userId === null) {
      throw new Error("Not signed in");
    }

    // Submit each response into the new survey_responses table.
    await Promise.all(
      responses.map(async (response) => {
        await ctx.db.insert("survey_responses", {
          response: response.body,
          userId,
          
          // timestamp: Date.now(),
        });
      })
    );
  },
});
