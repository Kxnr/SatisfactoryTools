export default {
  // TODO: set default background color, configurable bar color
  // TODO: configurable percent value

  template: `
    <q-btn  class="transition-colors bg-gradient-to-r from-[color:--q-primary] to-transparent" :class="['from-' + value_to_percent() + '%', 'to-' + value_to_percent() + '%']">
      <div class="border-10 px-1 bg-white rounded text-black" >{{ label }}</div>
    </button>
  `,
  name: 'ProgressButton',
  count: 4,
  props: {
    label: {
      type: String
    },
    value: {
      type: Number
    },
    min: {
      type: Number
    },
    max: {
      type: Number
    }
  },
  methods: {
    // TODO: animation
    // rounded to nearest 5 for compatibility with
    // tailwind gradient classes
    value_to_percent() {
      return Math.round((((this.value - this.min) / this.max) * 100) / 5) * 5;
    }
    
  },
  data () {
    console.log(this.value);
    console.log(this.min);
    console.log(this.max);
    return {
      label: this.label,
     }
  }
}

