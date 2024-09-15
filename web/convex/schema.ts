import { authTables } from "@convex-dev/auth/server";
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// The schema is normally optional, but Convex Auth
// requires indexes defined on `authTables`.
export default defineSchema({
  ...authTables,
  messages: defineTable({
    userId: v.id("users"),
    body: v.string(),
  }),
  tasks: defineTable({
    text: v.string(),
  }),
  survey_responses: defineTable({
    // surveyId: v.id("surveys"),
    userId: v.id("users"),
    response: v.string(),
  }),
});
