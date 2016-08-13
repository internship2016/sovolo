var gulp = require('gulp');
var sass = require('gulp-sass');
var less = require('gulp-less');
var notify = require('gulp-notify');
var bower = require('gulp-bower');
var gf = require('gulp-filter');
var mbf = require('main-bower-files');
var debug = require('gulp-debug');

var conf = {
  sassPath: './static/sass',
  scriptPath: './static/script',
  bowerDir: './bower_components'
};

gulp.task('bower.install', function () {
  return bower().pipe(gulp.dest(conf.bowerDir));
});

// TODO: minify/uglify/etc
gulp.task('bower.copy', function () {
  var filter = {
    js: gf('**/*.js', {restore: true}),
    css: gf('**/*.css', {restore: true}),
    less: gf('**/*.less', {restore: true}),
    fonts: gf([
      '**/*.eot',
      '**/*.woff',
      '**/*.woff2',
      '**/*.svg',
      '**/*.ttf'
    ], {restore: true})
  };

  return gulp.src(
    mbf({
      overrides: {
        bootstrap: {
          main: [
            './dist/js/bootstrap.js',
            './dist/css/*.min.*',
            './dist/fonts/*.*'
          ]
        }
      }
    })
  )

  .pipe(filter.js)
  .pipe(gulp.dest('./static/js'))
  .pipe(filter.js.restore)

  .pipe(filter.css)
  .pipe(gulp.dest('./static/css'))
  .pipe(filter.css.restore)

  .pipe(filter.less)
  .pipe(less())
  .pipe(gulp.dest('./static/css'))
  .pipe(filter.less.restore)

  .pipe(filter.fonts)
  .pipe(gulp.dest('./static/fonts'))
  .pipe(filter.fonts.restore)

  ;
});

gulp.task('bower', [
  'bower.install',
  'bower.copy'
]);

// Watch static/sass/style.scss,
// Compress all sass files into css
gulp.task('css', function () {
  return gulp.src(conf.sassPath + '/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('js', function () {
  return gulp.src(conf.scriptPath + '/*.js')
    .pipe(gulp.dest('./static/js'));
});

gulp.task('watch', function () {
  gulp.watch(conf.sassPath + '/**/*.scss', ['css']);
  gulp.watch(conf.scriptPath + '/**/*.js', ['js']);
});

gulp.task('default', ['bower', 'css', 'js']);
