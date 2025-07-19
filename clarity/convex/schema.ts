import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// The schema is entirely optional.
// You can delete this file (schema.ts) and the
// app will continue to work.
// The schema provides more precise TypeScript types.
export default defineSchema({
	// numbers: defineTable({
	//   value: v.number(),
	// }),
	games: defineTable({
		game_id: v.string(),
		rounds: v.number(),
		time_per_round: v.number(),
		player_ids: v.array(v.string()),
		creator_id: v.string(),
	}),
	players: defineTable({
		player_id: v.string(),
		display_name: v.string(),
	})
});
